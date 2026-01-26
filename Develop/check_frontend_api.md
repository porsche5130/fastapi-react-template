# 前端 API 響應檢查步驟

## 請在無痕瀏覽器的 Console 中執行以下命令：

### 1. 檢查最近一次 notifications API 的響應

在 Network 標籤中：
1. 找到最新的 `notifications` 請求
2. 點擊該請求
3. 查看 **Response** 標籤
4. 確認返回的 JSON 內容

### 2. 或者在 Console 標籤中手動呼叫 API

```javascript
// 取得 localStorage 中的 token
const token = localStorage.getItem('token');
console.log('Token:', token);

// 手動呼叫 API
fetch('http://localhost:10180/system_notifications/home/notifications', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log('=== API 響應 ===');
  console.log('通知數量:', data.notifications?.length || 0);
  console.log('完整響應:', data);
})
.catch(error => {
  console.error('API 錯誤:', error);
});
```

## 預期結果

### 如果關閉記錄存在（今日已關閉）
```json
{
  "notifications": []
}
```

### 如果關閉記錄不存在（應該顯示通知）
```json
{
  "notifications": [
    {
      "id": 1,
      "notice_csubject": "系統維護通知",
      ...
    }
  ]
}
```

## 請將以上結果截圖或複製給我
