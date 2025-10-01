"""Sensor platform for Tianxing API integration."""
import logging
import asyncio
import aiohttp
import async_timeout
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    DEVICE_NAME,
    DEVICE_MANUFACTURER,
    DEVICE_MODEL,
    RIDDLE_API_URL,
    JOKE_API_URL,
    MORNING_API_URL,
    EVENING_API_URL,
    POETRY_API_URL,
    SONG_CI_API_URL,
    YUAN_QU_API_URL,
    HISTORY_API_URL,
    SENTENCE_API_URL,
    COUPLET_API_URL,
    MAXIM_API_URL,
    CONF_API_KEY,
)

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=24)  # 每天更新一次

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    api_key = config_entry.data[CONF_API_KEY]
    
    # 创建设备信息
    device_info = DeviceInfo(
        identifiers={(DOMAIN, "tianxing_info_query")},
        name=DEVICE_NAME,
        manufacturer=DEVICE_MANUFACTURER,
        model=DEVICE_MODEL,
        configuration_url="https://www.tianapi.com/",
    )
    
    # 创建四个传感器实体
    sensors = [
        TianxingRiddleJokeSensor(api_key, device_info, config_entry.entry_id),
        TianxingMorningEveningSensor(api_key, device_info, config_entry.entry_id),
        TianxingPoetrySensor(api_key, device_info, config_entry.entry_id),
        TianxingDailyWordsSensor(api_key, device_info, config_entry.entry_id),
    ]
    
    async_add_entities(sensors, update_before_add=True)


class TianxingRiddleJokeSensor(SensorEntity):
    """天行数据谜语笑话传感器."""

    def __init__(self, api_key: str, device_info: DeviceInfo, entry_id: str):
        """Initialize the sensor."""
        self._api_key = api_key
        self._attr_name = "谜语笑话"
        self._attr_unique_id = f"{entry_id}_riddle_joke"
        self._attr_device_info = device_info
        self._attr_icon = "mdi:newspaper-variant"
        self._state = "等待更新"
        self._attributes = {}
        self._available = True

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    async def async_update(self):
        """Update sensor data."""
        try:
            # 获取谜语数据
            riddle_data = await self._fetch_riddle_data()
            # 获取笑话数据
            joke_data = await self._fetch_joke_data()
            
            if riddle_data and joke_data:
                # 处理数据
                riddle_result = riddle_data.get("result", {})
                joke_list = joke_data.get("result", {}).get("list", [])
                
                if joke_list:
                    joke_result = joke_list[0]
                else:
                    joke_result = {}
                
                self._state = riddle_result.get("riddle", "未知谜语")
                self._available = True
                
                # 设置属性
                self._attributes = {
                    "title": "谜语笑话",
                    "code": joke_data.get("code", 0),
                    "riddle": {
                        "subtitle": "每日谜语",
                        "content": riddle_result.get("riddle", ""),
                        "type": riddle_result.get("type", ""),
                        "answer": riddle_result.get("answer", ""),
                        "description": riddle_result.get("description", ""),
                        "disturb": riddle_result.get("disturb", "")
                    },
                    "joke": {
                        "subtitle": "每日笑话",
                        "name": joke_result.get("title", ""),
                        "content": joke_result.get("content", "")
                    },
                    "update_time": self._get_current_time()
                }
                
                _LOGGER.info("天行数据谜语笑话更新成功")
                
            else:
                self._available = False
                self._state = "API请求失败"
                _LOGGER.error("无法获取天行数据谜语笑话，请检查API密钥是否正确")
                
        except Exception as e:
            _LOGGER.error("更新天行数据谜语笑话传感器时出错: %s", e)
            self._available = False
            self._state = f"更新失败: {str(e)}"

    async def _fetch_riddle_data(self):
        """获取谜语数据."""
        url = f"{RIDDLE_API_URL}?key={self._api_key}"
        return await self._fetch_api_data(url)

    async def _fetch_joke_data(self):
        """获取笑话数据."""
        url = f"{JOKE_API_URL}?key={self._api_key}&num=1"
        return await self._fetch_api_data(url)

    async def _fetch_api_data(self, url: str):
        """获取API数据."""
        session = async_get_clientsession(self.hass)
        
        try:
            async with async_timeout.timeout(15):
                response = await session.get(url)
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("API响应: %s", data)
                    
                    # 检查API返回的错误码
                    if data.get("code") == 200:
                        return data
                    elif data.get("code") == 100:  # 常见错误码
                        _LOGGER.error("API密钥错误: %s", data.get("msg", "未知错误"))
                    else:
                        _LOGGER.error("API返回错误[%s]: %s", data.get("code"), data.get("msg", "未知错误"))
                else:
                    _LOGGER.error("HTTP请求失败: %s", response.status)
        except asyncio.TimeoutError:
            _LOGGER.error("API请求超时")
        except Exception as e:
            _LOGGER.error("获取API数据时出错: %s", e)
        
        return None

    def _get_current_time(self):
        """获取当前时间字符串."""
        from datetime import datetime
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")


class TianxingMorningEveningSensor(SensorEntity):
    """天行数据早安晚安传感器."""

    def __init__(self, api_key: str, device_info: DeviceInfo, entry_id: str):
        """Initialize the sensor."""
        self._api_key = api_key
        self._attr_name = "早安晚安"
        self._attr_unique_id = f"{entry_id}_morning_evening"
        self._attr_device_info = device_info
        self._attr_icon = "mdi:weather-sunset"
        self._state = "等待更新"
        self._attributes = {}
        self._available = True

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    async def async_update(self):
        """Update sensor data."""
        try:
            # 获取早安数据
            morning_data = await self._fetch_morning_data()
            # 获取晚安数据
            evening_data = await self._fetch_evening_data()
            
            if morning_data and evening_data:
                # 处理数据
                morning_content = morning_data.get("result", {}).get("content", "")
                evening_content = evening_data.get("result", {}).get("content", "")
                
                # 处理早安内容
                if not morning_content or morning_content == "":
                    morning_content = "早安！新的一天开始了！"
                elif not morning_content.startswith("早安"):
                    morning_content = f"早安！{morning_content}"
                
                # 处理晚安内容
                if not evening_content or evening_content == "":
                    evening_content = "晚安！好梦！"
                elif not evening_content.endswith("晚安"):
                    evening_content = f"{evening_content}晚安！"
                
                self._state = morning_content[:50] + "..." if len(morning_content) > 50 else morning_content
                self._available = True
                
                # 设置属性
                self._attributes = {
                    "title": "早安晚安",
                    "code": evening_data.get("code", 0),
                    "mtitle": "早安心语",
                    "morning": morning_content,
                    "etitle": "晚安心语",
                    "evening": evening_content,
                    "update_time": self._get_current_time()
                }
                
                _LOGGER.info("天行数据早安晚安更新成功")
                
            else:
                self._available = False
                self._state = "API请求失败"
                _LOGGER.error("无法获取天行数据早安晚安，请检查API密钥是否正确")
                
        except Exception as e:
            _LOGGER.error("更新天行数据早安晚安传感器时出错: %s", e)
            self._available = False
            self._state = f"更新失败: {str(e)}"

    async def _fetch_morning_data(self):
        """获取早安数据."""
        url = f"{MORNING_API_URL}?key={self._api_key}"
        return await self._fetch_api_data(url)

    async def _fetch_evening_data(self):
        """获取晚安数据."""
        url = f"{EVENING_API_URL}?key={self._api_key}"
        return await self._fetch_api_data(url)

    async def _fetch_api_data(self, url: str):
        """获取API数据."""
        session = async_get_clientsession(self.hass)
        
        try:
            async with async_timeout.timeout(15):
                response = await session.get(url)
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("API响应: %s", data)
                    
                    # 检查API返回的错误码
                    if data.get("code") == 200:
                        return data
                    elif data.get("code") == 100:  # 常见错误码
                        _LOGGER.error("API密钥错误: %s", data.get("msg", "未知错误"))
                    else:
                        _LOGGER.error("API返回错误[%s]: %s", data.get("code"), data.get("msg", "未知错误"))
                else:
                    _LOGGER.error("HTTP请求失败: %s", response.status)
        except asyncio.TimeoutError:
            _LOGGER.error("API请求超时")
        except Exception as e:
            _LOGGER.error("获取API数据时出错: %s", e)
        
        return None

    def _get_current_time(self):
        """获取当前时间字符串."""
        from datetime import datetime
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")


class TianxingPoetrySensor(SensorEntity):
    """天行数据古诗宋词传感器."""

    def __init__(self, api_key: str, device_info: DeviceInfo, entry_id: str):
        """Initialize the sensor."""
        self._api_key = api_key
        self._attr_name = "古诗宋词"
        self._attr_unique_id = f"{entry_id}_poetry"
        self._attr_device_info = device_info
        self._attr_icon = "mdi:book-open-variant"
        self._state = "等待更新"
        self._attributes = {}
        self._available = True

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    async def async_update(self):
        """Update sensor data."""
        try:
            # 获取唐诗数据
            poetry_data = await self._fetch_poetry_data()
            # 获取宋词数据
            song_ci_data = await self._fetch_song_ci_data()
            # 获取元曲数据
            yuan_qu_data = await self._fetch_yuan_qu_data()
            
            if poetry_data and song_ci_data and yuan_qu_data:
                # 处理数据
                poetry_list = poetry_data.get("result", {}).get("list", [])
                song_ci_result = song_ci_data.get("result", {})
                yuan_qu_list = yuan_qu_data.get("result", {}).get("list", [])
                
                # 获取第一条数据
                poetry_first = poetry_list[0] if poetry_list else {}
                yuan_qu_first = yuan_qu_list[0] if yuan_qu_list else {}
                
                # 设置状态为唐诗内容
                self._state = poetry_first.get("content", "未知诗词")[:50] + "..." if len(poetry_first.get("content", "")) > 50 else poetry_first.get("content", "未知诗词")
                self._available = True
                
                # 设置属性
                self._attributes = {
                    "title": "古诗宋词",
                    "code": song_ci_data.get("code", 0),
                    "tangshi": {
                        "subtitle": "唐诗鉴赏",
                        "content": poetry_first.get("content", ""),
                        "source": poetry_first.get("title", ""),
                        "author": poetry_first.get("author", ""),
                        "intro": poetry_first.get("intro", ""),
                        "kind": poetry_first.get("kind", "")
                    },
                    "songci": {
                        "subtitle": "最美宋词",
                        "content": song_ci_result.get("content", ""),
                        "source": song_ci_result.get("source", ""),
                        "author": song_ci_result.get("author", "")
                    },
                    "yuanqu": {
                        "subtitle": "精选元曲",
                        "content": yuan_qu_first.get("content", ""),
                        "source": yuan_qu_first.get("title", ""),
                        "author": yuan_qu_first.get("author", ""),
                        "note": yuan_qu_first.get("note", ""),
                        "translation": yuan_qu_first.get("translation", "")
                    },
                    "update_time": self._get_current_time()
                }
                
                _LOGGER.info("天行数据古诗宋词更新成功")
                
            else:
                self._available = False
                self._state = "API请求失败"
                _LOGGER.error("无法获取天行数据古诗宋词，请检查API密钥是否正确")
                
        except Exception as e:
            _LOGGER.error("更新天行数据古诗宋词传感器时出错: %s", e)
            self._available = False
            self._state = f"更新失败: {str(e)}"

    async def _fetch_poetry_data(self):
        """获取唐诗数据."""
        url = f"{POETRY_API_URL}?key={self._api_key}"
        return await self._fetch_api_data(url)

    async def _fetch_song_ci_data(self):
        """获取宋词数据."""
        url = f"{SONG_CI_API_URL}?key={self._api_key}"
        return await self._fetch_api_data(url)

    async def _fetch_yuan_qu_data(self):
        """获取元曲数据."""
        url = f"{YUAN_QU_API_URL}?key={self._api_key}&num=1&page=1"
        return await self._fetch_api_data(url)

    async def _fetch_api_data(self, url: str):
        """获取API数据."""
        session = async_get_clientsession(self.hass)
        
        try:
            async with async_timeout.timeout(15):
                response = await session.get(url)
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("API响应: %s", data)
                    
                    # 检查API返回的错误码
                    if data.get("code") == 200:
                        return data
                    elif data.get("code") == 100:  # 常见错误码
                        _LOGGER.error("API密钥错误: %s", data.get("msg", "未知错误"))
                    else:
                        _LOGGER.error("API返回错误[%s]: %s", data.get("code"), data.get("msg", "未知错误"))
                else:
                    _LOGGER.error("HTTP请求失败: %s", response.status)
        except asyncio.TimeoutError:
            _LOGGER.error("API请求超时")
        except Exception as e:
            _LOGGER.error("获取API数据时出错: %s", e)
        
        return None

    def _get_current_time(self):
        """获取当前时间字符串."""
        from datetime import datetime
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")


class TianxingDailyWordsSensor(SensorEntity):
    """天行数据每日一言传感器."""

    def __init__(self, api_key: str, device_info: DeviceInfo, entry_id: str):
        """Initialize the sensor."""
        self._api_key = api_key
        self._attr_name = "每日一言"
        self._attr_unique_id = f"{entry_id}_daily_words"
        self._attr_device_info = device_info
        self._attr_icon = "mdi:comment-quote"
        self._state = "等待更新"
        self._attributes = {}
        self._available = True

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    async def async_update(self):
        """Update sensor data."""
        try:
            # 获取历史数据
            history_data = await self._fetch_history_data()
            # 获取名句数据
            sentence_data = await self._fetch_sentence_data()
            # 获取对联数据
            couplet_data = await self._fetch_couplet_data()
            # 获取格言数据
            maxim_data = await self._fetch_maxim_data()
            
            if history_data and sentence_data and couplet_data and maxim_data:
                # 处理数据
                history_result = history_data.get("result", {})
                sentence_result = sentence_data.get("result", {})
                couplet_result = couplet_data.get("result", {})
                maxim_result = maxim_data.get("result", {})
                
                # 设置状态为历史内容
                self._state = history_result.get("content", "未知内容")[:50] + "..." if len(history_result.get("content", "")) > 50 else history_result.get("content", "未知内容")
                self._available = True
                
                # 设置属性
                self._attributes = {
                    "title": "每日一言",
                    "history": {
                        "subtitle": "简说历史",
                        "content": history_result.get("content", "")
                    },
                    "sentence": {
                        "subtitle": "古籍名句",
                        "content": sentence_result.get("content", ""),
                        "source": sentence_result.get("source", "")
                    },
                    "couplet": {
                        "subtitle": "经典对联",
                        "content": couplet_result.get("content", "")
                    },
                    "maxim": {
                        "subtitle": "英文格言",
                        "content": maxim_result.get("en", ""),
                        "translate": maxim_result.get("zh", "")
                    },
                    "update_time": self._get_current_time()
                }
                
                _LOGGER.info("天行数据每日一言更新成功")
                
            else:
                self._available = False
                self._state = "API请求失败"
                _LOGGER.error("无法获取天行数据每日一言，请检查API密钥是否正确")
                
        except Exception as e:
            _LOGGER.error("更新天行数据每日一言传感器时出错: %s", e)
            self._available = False
            self._state = f"更新失败: {str(e)}"

    async def _fetch_history_data(self):
        """获取历史数据."""
        url = f"{HISTORY_API_URL}?key={self._api_key}"
        return await self._fetch_api_data(url)

    async def _fetch_sentence_data(self):
        """获取名句数据."""
        url = f"{SENTENCE_API_URL}?key={self._api_key}"
        return await self._fetch_api_data(url)

    async def _fetch_couplet_data(self):
        """获取对联数据."""
        url = f"{COUPLET_API_URL}?key={self._api_key}"
        return await self._fetch_api_data(url)

    async def _fetch_maxim_data(self):
        """获取格言数据."""
        url = f"{MAXIM_API_URL}?key={self._api_key}"
        return await self._fetch_api_data(url)

    async def _fetch_api_data(self, url: str):
        """获取API数据."""
        session = async_get_clientsession(self.hass)
        
        try:
            async with async_timeout.timeout(15):
                response = await session.get(url)
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("API响应: %s", data)
                    
                    # 检查API返回的错误码
                    if data.get("code") == 200:
                        return data
                    elif data.get("code") == 100:  # 常见错误码
                        _LOGGER.error("API密钥错误: %s", data.get("msg", "未知错误"))
                    else:
                        _LOGGER.error("API返回错误[%s]: %s", data.get("code"), data.get("msg", "未知错误"))
                else:
                    _LOGGER.error("HTTP请求失败: %s", response.status)
        except asyncio.TimeoutError:
            _LOGGER.error("API请求超时")
        except Exception as e:
            _LOGGER.error("获取API数据时出错: %s", e)
        
        return None

    def _get_current_time(self):
        """获取当前时间字符串."""
        from datetime import datetime
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")