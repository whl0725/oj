// 导出一个名为formatDate的函数，用于格式化日期字符串
export function formatDate(dateString) {
  // 将输入的日期字符串转换为Date对象
  const date = new Date(dateString)
  // 获取年份
  const year = date.getFullYear()
  // 获取月份，由于getMonth返回的月份是从0开始的，所以需要加1
  // 使用String将其转换为字符串，并使用padStart方法确保月份始终为两位数，不足两位前面补0
  const month = String(date.getMonth() + 1).padStart(2, '0')
  // 获取日期
  // 使用String将其转换为字符串，并使用padStart方法确保日期始终为两位数，不足两位前面补0
  const day = String(date.getDate()).padStart(2, '0')
  // 获取小时
  // 使用String将其转换为字符串，并使用padStart方法确保小时始终为两位数，不足两位前面补0
  const hours = String(date.getHours()).padStart(2, '0')
  // 获取分钟
  // 使用String将其转换为字符串，并使用padStart方法确保分钟始终为两位数，不足两位前面补0
  const minutes = String(date.getMinutes()).padStart(2, '0')
  
  // 返回格式化后的日期字符串，格式为YYYY-MM-DD HH:mm
  return `${year}-${month}-${day} ${hours}:${minutes}`
} 