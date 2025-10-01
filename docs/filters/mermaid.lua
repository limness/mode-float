local utils = require 'pandoc.utils'

local function has_class(el, class)
  for _, c in ipairs(el.classes) do if c == class then return true end end
  return false
end

local function ensure_dir(path) os.execute(string.format('mkdir -p "%s"', path)) end
local function file_exists(path) local f=io.open(path,"rb"); if f then f:close(); return true end; return false end

function CodeBlock(el)
  if not has_class(el, 'mermaid') then return nil end

  local outdir = os.getenv('MERMAID_OUTDIR') or 'static/mermaid'
  ensure_dir(outdir)

  local sha = (utils.sha1 and utils.sha1(el.text) or tostring(el.text):gsub("%W",""))
  local stem = string.format("mermaid-%s", sha:sub(1,16))
  local mmd  = outdir .. "/" .. stem .. ".mmd"
  local png  = outdir .. "/" .. stem .. ".png"

  local widthpx = el.attributes['widthpx'] or '1200'
  if not file_exists(png) then
    local f = io.open(mmd, "w"); f:write(el.text); f:close()
    os.execute(string.format('mmdc -i "%s" -o "%s" -b transparent -w %s 1>/dev/null 2>&1', mmd, png, widthpx))
    if not file_exists(png) then
      io.stderr:write("[mermaid.lua] mmdc failed for ", mmd, "\n"); return nil
    end
    os.remove(mmd)
  end

  local img = io.open(png, "rb"); local bytes = img:read("*all"); img:close()
  pandoc.mediabag.insert(png, "image/png", bytes)

  local attrs = {}
  attrs['width']  = el.attributes['width']  or '100%'
  if el.attributes['maxheight'] then
    attrs['height'] = el.attributes['maxheight']
  elseif el.attributes['height'] then
    attrs['height'] = el.attributes['height']
  end

  return pandoc.Para{ pandoc.Image({}, png, "", pandoc.Attr("", {}, attrs)) }
end
