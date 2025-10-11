# 天聚数行API Home Assistant 集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

这是一个为 Home Assistant 开发的定制集成，用于从[天聚数行](https://www.tianapi.com/)获取各类文化资讯内容，包括谜语笑话、早安晚安、古诗宋词和每日一言等。

## 功能特点

- 🌅 **早安晚安** - 早安心语和晚安心语
- 📜 **古诗宋词** - 唐诗、宋词、元曲鉴赏
- 🎭 **每日一言** - 历史知识、古籍名句、经典对联和英文格言
- 💬 **滚动内容** - 分时段更新上述4个数据实体
- **属性**:
  - `title`: 内容标题（带表情符号）
  - `subtitle`: 副标题
  - `content1`: HTML格式内容（使用`<br>`换行）
  - `content2`: 纯文本格式内容（使用`\n`换行）
  - `voicetitle`: 语音播报标题
  - `align`: 主标题对齐方式
  - `subalign`: 副标题对齐方式
  - `time_slot`: 当前时间段名称
  - `update_time`: 最后更新时间

#### 时间段配置
滚动内容会根据一天中的不同时间段自动切换显示内容：

| 时间段 | 内容类型 | 时间范围 |
|--------|----------|----------|
| 早安时段 | 早安问候 | 05:30-08:29 |
| 格言时段 | 英文格言 | 08:30-10:59 |
| 名句时段 | 古籍名句 | 13:00-13:59 |
| 对联时段 | 经典对联 | 14:00-14:59 |
| 历史时段 | 简说历史 | 15:00-16:59 |
| 唐诗时段 | 唐诗鉴赏 | 17:00-18:29 |
| 宋词时段 | 最美宋词 | 18:30-20:29 |
| 元曲时段 | 精选元曲 | 20:30-20:59 |
| 晚安时段 | 晚安问候 | 22:00-05:29 |

## 安装前准备

### 1. 获取 API 密钥

在使用本集成前，您需要先申请天聚数行的 API 密钥：

1. 访问 [天聚数行官网](https://www.tianapi.com/)
2. 注册账号并登录
3. 进入控制台，申请 API 密钥
4. 确保您的账户有足够的调用次数（免费版本通常有每日限制）

### 2. 启用自定义集成

Home Assistant 需要启用自定义集成功能：

1. 确保您的 Home Assistant 实例可以访问互联网
2. 确认已启用高级模式（在用户配置文件中设置）

## 安装方法
### 方法一：通过 HACS 安装（推荐）
1. 确保已安装 [HACS](https://hacs.xyz/)
2. 在 HACS 的 "Integrations" 页面，点击右上角的三个点菜单，选择 "Custom repositories"
3. 在弹出窗口中添加仓库地址：https://github.com/lambilly/hass_tian_api/ ，类别选择 "Integration"
4. 在 HACS 中搜索 "天聚数行API"
5. 点击下载
6. 重启 Home Assistant

### 方法二：手动安装
1. 下载本集成文件
2. 将 `custom_components/tian_api` 文件夹复制到您的 Home Assistant 配置目录中的 `custom_components` 文件夹内
3. 重启 Home Assistant

## 配置步骤

### 1. 添加集成

1. 进入 Home Assistant 的 **设置** → **设备与服务** → **集成**
2. 点击右下角的 **添加集成** 按钮
3. 搜索 "天聚数行API"
4. 点击进入配置界面

### 2. 输入 API 密钥

1. 在弹出的对话框中输入您从天聚数行获取的 API 密钥
2. API 密钥应为 32 位字符串
3. 点击 **提交**

### 3. 完成安装

集成会自动创建以下实体：

- `sensor.gun_dong_nei_rong` - 滚动内容
- `sensor.zao_an_wan_an` - 早安晚安  
- `sensor.gu_shi_song_ci` - 古诗宋词
- `sensor.mei_ri_yi_yan` - 每日一言

所有实体都会归属于名为 **"天聚信息查询"** 的设备。

## 实体属性说明

### 早安晚安实体
- **状态**: 最后更新时间
- **属性**:
  - `morning`: 完整的早安心语
  - `evening`: 完整的晚安心语
  - `update_time`: 最后更新时间

### 古诗宋词实体
- **状态**: 最后更新时间
- **属性**:
  - `tangshi`: 唐诗详细信息（内容、作者、注释等）
  - `songci`: 宋词详细信息
  - `yuanqu`: 元曲详细信息
  - `update_time`: 最后更新时间

### 每日一言实体
- **状态**: 最后更新时间
- **属性**:
  - `history`: 简说历史内容
  - `sentence`: 古籍名句
  - `couplet`: 经典对联
  - `maxim`: 英文格言（含中文翻译）
  - `update_time`: 最后更新时间

## 自动化示例

### 每日早安播报
```yaml
automation:
  - alias: "Morning Greeting"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: tts.speak
        data:
          message: "{{ state_attr('sensor.zao_an_wan_an', 'morning') }}"
```

### 桌面通知显示每日一言
```yaml
automation:
  - alias: "Daily Wisdom Notification"
    trigger:
      - platform: time
        at: "09:00:00"
    action:
      - service: notify.persistent_notification
        data:
          message: >
            今日智慧：
            历史：{{ state_attr('sensor.mei_ri_yi_yan', 'history')['content'] }}
            名句：{{ state_attr('sensor.mei_ri_yi_yan', 'sentence')['content'] }}
          title: "每日一言"
```

## 故障排除

### 常见问题

1. **集成无法加载**
   - 检查 API 密钥格式是否正确（32位字符串）
   - 确认网络连接正常
   - 查看 Home Assistant 日志获取详细错误信息

2. **数据不更新**
   - 确认 API 密钥有效且未过期
   - 检查天聚数行账户的调用次数限制
   - 等待下一个自动更新周期（24小时）

3. **实体不可用**
   - 重启 Home Assistant
   - 检查自定义集成文件夹权限
   - 确认所有依赖文件完整

### 查看日志

如需调试，请在 `configuration.yaml` 中添加：

```yaml
logger:
  default: info
  logs:
    custom_components.tianxing_api: debug
```

## API 调用说明

本集成使用以下天聚数行 API 接口：

- `zaoan/index` - 早安
- `wanan/index` - 晚安
- `poetry/index` - 唐诗
- `zmsc/index` - 宋词
- `yuanqu/index` - 元曲
- `pitlishi/index` - 历史
- `gjmj/index` - 名句
- `duilian/index` - 对联
- `enmaxim/index` - 英文格言

## 技术支持

如有问题，请：

1. 查看本 README 文档
2. 检查 Home Assistant 日志
3. 访问 [天聚数行官方文档](https://www.tianapi.com/)
4. 在项目 Issues 页面提交问题

## 版本历史

- v1.0.0 - 初始版本，集成四个主要功能模块
- v1.1.0 - 第二版本，增加滚动内容实体整合时段显示
- v1.1.2 - 第三版本，删除两个API接口减少到9个，符合天聚数行1免费申请0个以下API
【后续本仓库不再更新，只更新免费版https://github.com/lambilly/hass_tian_free】

## 免责声明

本集成为第三方开发，与天聚数行官方无关。使用本集成需要遵守天聚数行的 API 使用条款和调用限制。
