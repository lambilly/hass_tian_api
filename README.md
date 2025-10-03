# 天聚数行API Home Assistant 集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

这是一个为 Home Assistant 开发的定制集成，用于从[天聚数行](https://www.tianapi.com/)获取各类文化资讯内容，包括谜语笑话、早安晚安、古诗宋词和每日一言等。

## 功能特点

- 🎭 **谜语笑话** - 每日谜语和笑话
- 🌅 **早安晚安** - 早安心语和晚安心语
- 📜 **古诗宋词** - 唐诗、宋词、元曲鉴赏
- 💬 **每日一言** - 历史知识、古籍名句、经典对联和英文格言

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
3. 在弹出窗口中添加仓库地址：https://github.com/lambilly/hass_tian_api，类别选择 "Integration"
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

- `sensor.mi_yu_xiao_hua` - 谜语笑话
- `sensor.zao_an_wan_an` - 早安晚安  
- `sensor.gu_shi_song_ci` - 古诗宋词
- `sensor.mei_ri_yi_yan` - 每日一言

所有实体都会归属于名为 **"天聚信息查询"** 的设备。

## 实体属性说明

### 谜语笑话实体
- **状态**: 最后更新时间
- **属性**:
  - `riddle`: 谜语详细信息（内容、答案、类型等）
  - `joke`: 笑话详细信息（标题、内容）
  - `update_time`: 最后更新时间

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

- `caizimi/index` - 谜语
- `joke/index` - 笑话
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

## 免责声明

本集成为第三方开发，与天聚数行官方无关。使用本集成需要遵守天聚数行的 API 使用条款和调用限制。
