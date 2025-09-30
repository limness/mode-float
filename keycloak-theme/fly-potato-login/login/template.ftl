<#macro layout bodyClass title>
<!DOCTYPE html>
<html lang="${locale.currentLanguage!"en"}">
<head>
    <meta charset="utf-8" />
    <title>${title?html}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="stylesheet" href="${url.resourcesPath}/css/theme.css" />
</head>
<body class="fly-potato-login ${bodyClass}">
    <div class="auth-wrapper">
        <#nested>
    </div>
</body>
</html>
</#macro>

<#macro registrationLayout bodyClass title>
<@layout bodyClass=bodyClass title=title>
    <div class="auth-card">
        <#nested>
    </div>
</@layout>
</#macro>
