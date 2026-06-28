/**
 * CPYCMS - 前端版本信息。
 * 版本号读取自 package.json，统一用于页面展示和构建校验。
 */

import packageInfo from '../package.json'

export const APP_VERSION = packageInfo.version
