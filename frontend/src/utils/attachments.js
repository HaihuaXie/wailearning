export const MAX_ATTACHMENT_SIZE = 20 * 1024 * 1024

const BLOCKED_ATTACHMENT_EXTENSIONS = ['.apk', '.app', '.bat', '.cmd', '.com', '.exe', '.msi', '.ps1', '.scr']

export const attachmentHintText = '支持压缩包、Office 文档、PDF、TXT、图片等常见格式，禁止 .exe，可选，最大 20 MB。'

export const validateAttachmentFile = file => {
  if (!file) {
    return { valid: false, message: '请选择一个附件文件。' }
  }

  const fileName = file.name || ''
  const extension = fileName.includes('.') ? fileName.slice(fileName.lastIndexOf('.')).toLowerCase() : ''

  if (BLOCKED_ATTACHMENT_EXTENSIONS.includes(extension)) {
    return { valid: false, message: '不支持上传可执行文件。' }
  }

  if (file.size > MAX_ATTACHMENT_SIZE) {
    return { valid: false, message: '附件大小不能超过 20 MB。' }
  }

  return { valid: true }
}
