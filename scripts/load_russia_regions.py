#!/usr/bin/env python3

import asyncio
import aiohttp
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SHP_URL = "https://github.com/Ar4ikov/Russia-Admin-Shapemap/raw/main/RF/admin_4.shp"
DBF_URL = "https://github.com/Ar4ikov/Russia-Admin-Shapemap/raw/main/RF/admin_4.dbf"

API_BASE_URL = "http://backend:8000"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/api/v1/regions/upload-shapefile"

MAX_RETRIES = 15
RETRY_DELAY = 20


async def download_file(session: aiohttp.ClientSession, url: str, filename: str) -> bytes:
    logger.info(f"Downloading file: {filename}")
    
    for attempt in range(MAX_RETRIES):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    logger.info(f"File {filename} downloaded successfully ({len(content)} bytes)")
                    return content
                else:
                    logger.warning(f"Error downloading {filename}: HTTP {response.status}")
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} to download {filename} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
            else:
                raise
    
    raise Exception(f"Failed to download file {filename} after {MAX_RETRIES} attempts")


async def upload_to_api(session: aiohttp.ClientSession, shp_content: bytes, dbf_content: bytes) -> bool:
    logger.info("Uploading files to API...")
    
    data = aiohttp.FormData()
    data.add_field('shp', shp_content, filename='admin_4.shp', content_type='application/octet-stream')
    data.add_field('dbf', dbf_content, filename='admin_4.dbf', content_type='application/octet-stream')
    
    for attempt in range(MAX_RETRIES):
        try:
            async with session.post(UPLOAD_ENDPOINT, data=data) as response:
                if response.status == 201:
                    result = await response.json()
                    logger.info(f"Files successfully uploaded to API: {result}")
                    return True
                else:
                    error_text = await response.text()
                    logger.warning(f"API error (HTTP {response.status}): {error_text}")
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} to upload to API failed: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
            else:
                raise
    
    return False


async def wait_for_api(session: aiohttp.ClientSession, timeout: int = 300) -> bool:
    logger.info("Waiting for API to be ready...")
    
    start_time = asyncio.get_event_loop().time()
    
    while (asyncio.get_event_loop().time() - start_time) < timeout:
        try:
            async with session.get(f"{API_BASE_URL}/health") as response:
                if response.status == 200:
                    logger.info("API is ready")
                    return True
        except Exception:
            pass
        
        await asyncio.sleep(5)
    
    logger.warning(f"API not ready after {timeout} seconds of waiting")
    return False


async def main():
    logger.info("Starting Russia regions data loading...")
    
    timeout = aiohttp.ClientTimeout(total=300)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            if not await wait_for_api(session):
                logger.error("API unavailable, skipping data loading")
                return False

            shp_task = download_file(session, SHP_URL, "admin_4.shp")
            dbf_task = download_file(session, DBF_URL, "admin_4.dbf")
            
            shp_content, dbf_content = await asyncio.gather(shp_task, dbf_task)
            
            success = await upload_to_api(session, shp_content, dbf_content)
            
            if success:
                logger.info("Russia regions data loaded successfully!")
                return True
            else:
                logger.error("Failed to load data into API")
                return False
                
        except Exception as e:
            logger.error(f"Error during data loading: {e}")
            return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Data loading interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)
