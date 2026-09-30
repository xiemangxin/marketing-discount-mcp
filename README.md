# 行銷文案折扣計算 MCP

給行銷人員透過 AI 計算指定商品的最低／最高折數、省%範圍及可用文案。此專案保留本機 stdio MCP 伺服器，並新增可部署至 GitHub Pages 的純前端網頁版（docs/）。網頁版與 MCP 各自獨立執行。

## 功能與定義

- `calculate_discount_range`：可輸入 1–1000 件商品，輸出個別折扣、區間、對應商品 ID、條件與文案。
- `convert_discount`：換算「8 折」與「20% OFF」。
- 折數 = 優惠價 ÷ 原價 × 10；數字越低，優惠越大。
- 省% = (1 − 優惠價 ÷ 原價) × 100；數字越高，優惠越大。
- 「最低折數」對應「最大省%」；工具不使用容易誤解的「最高折扣」作欄位。
- 精確運算使用有理數。折數向上取至小數 2 位、省%向下取至小數 2 位，避免放大優惠；同時回傳精確售價比例。
- 僅以輸入商品計算，不自動宣稱全館、不計平均折扣。所有商品都未降價時，不產生促銷折扣話術。

## 安裝（Python 3.10 以上）

解壓縮至固定資料夾，例如 `C:\tools\discount-mcp`，在該資料夾執行：

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS／Linux：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

依官方 Python SDK v1 FastMCP API 實作，使用 `<2` 上界防止升級到不相容的大版本。此交付實測版本為 mcp 1.30.0；要重現此版本可安裝 `mcp==1.30.0`。
官方文件：https://py.sdk.modelcontextprotocol.io/v1/

## 接上支援本機 stdio 的 MCP 用戶端

把 `mcp-config.example.json` 的兩個路徑改成自己的絕對路徑，依用戶端設定方式加入 MCP 伺服器。不同用戶端的外層設定格式可能不同；command 和 args 指向下列程式即可。Python 必須使用上一步虛擬環境的執行檔。

```json
{
  "mcpServers": {
    "marketing-discount": {
      "command": "C:\\tools\\discount-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\tools\\discount-mcp\\server.py"]
    }
  }
}
```

此版本只有本機 stdio，不能把上述本機路徑當成遠端 MCP URL。若使用僅支援遠端連線的平台，需另行部署 HTTP 版本與存取控制。

## 行銷人員怎麼問

「香水原價 1,000、優惠價 790；保養品原價 2,000、優惠價 1,000。都是會員輸碼優惠，幫我算最低幾折、最高省幾％，寫三種標題。」

AI 呼叫 `calculate_discount_range`：

```json
{
  "products": [
    {"id":"A","name":"香水","original_price":"1000","sale_price":"790"},
    {"id":"B","name":"保養品","original_price":"2000","sale_price":"1000"}
  ],
  "currency":"TWD",
  "conditions":"會員輸碼優惠"
}
```

結果：最低 5 折、最高 7.9 折；省 21%–50%；最大優惠商品 B。
文案例：「指定商品（會員輸碼優惠）低至 5 折」、「指定商品（會員輸碼優惠）最高省 50%」。

換算範例：`convert_discount(value="21", input_type="percent_off")` → 7.9 折。

## 輸入與使用範圍

- 價格用純數字字串，例如 `"1299.50"`；不要輸入 `$1,299`。最多六位小數、最大 10^15。
- 原價必須大於零；優惠價不得負數或高於原價。價格不合法會回傳 MCP 工具錯誤，不會默默略過該商品。
- 每件商品 ID 必須唯一；名稱不能空白；不接受未定義商品欄位。
- 同一次呼叫必須為相同幣別與適用條件；若條件不同，分次呼叫。
- `conditions` 必須填寫會員、滿額、輸碼、限量等必要條件。工具不能從售價自行得知未輸入的限制。
- 優惠價須為已確認的實付價格；本版不推算滿額門檻、折上折順序、購物籃分攤、運費、點數、信用卡回饋或贈品價值。
- 不判定原價基準是否合宜、庫存是否充足；最終發布前依實際活動資料核對。
- 全程本機計算，不發送商品資料到外部服務。AI 用戶端自身的資料處理依其設定。

## 驗證

```sh
python -m unittest discover -s . -p test_calculator.py -v
python test_mcp.py
```

第一項檢查折扣區間、同折扣商品、保守取位、換算、零元／無折扣、非法資料。
第二項啟動真實 MCP 子程序，驗證初始化、工具列舉、呼叫與錯誤回傳。

檔案：server.py（MCP）、calculator.py（計算核心）、requirements.txt（依賴）、test_calculator.py、test_mcp.py、mcp-config.example.json。


## 網頁版 / GitHub Pages

`docs/` 內含完整靜態網頁，不需 npm 安裝或後端服務。以 BigInt 精確運算價格與比例，保持 Python MCP 的保守取位規則。支援商品增刪、活動條件、幣別標記、文案複製、商品明細與折數/OFF 換算。商品資料只存在目前頁面記憶體；重新整理會清除。

### 發布

1. 建立專用 GitHub repository，例如 `marketing-discount-mcp`。
2. 將此資料夾的全部檔案上傳至 `main`（保留 docs 資料夾）。
3. Settings → Pages → Build and deployment → Deploy from a branch。
4. 選 `main` 與 `/docs`，Save。
5. 等待 Pages 部署完成，使用 Settings → Pages 顯示的正式網址。

Pages 僅提供網頁版，不會執行 Python 或提供遠端 MCP endpoint；原本 MCP 仍依前述步驟安裝使用。免費帳號可使用公開儲存庫；私有儲存庫是否可用 Pages 依 GitHub 方案而定。

### 本機預覽與驗證

```sh
python -m http.server 8000 --directory docs
# 開啟 http://localhost:8000
python -m unittest discover -s . -p test_calculator.py -v
python test_web_parity.py
```

網頁接受非負純數字（最多六位小數，不含千分位、貨幣符號或科學記號）。`test_web_parity.py` 需 Node.js，用 106 組邊界與隨機商品案例對照原始 Python 核心。
