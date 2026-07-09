# Tài liệu hướng dẫn viết Script Kiểm thử Katalon Studio cho LancerAI

Tài liệu này cung cấp mã nguồn kiểm thử tự động API (API Auto Test) bằng **Katalon Studio** cho trường hợp sử dụng (Use case): **Khởi tạo phiên phỏng vấn thành công**.

---

## 1. Khai báo Web Service Request (Object Repository)

Trong Katalon Studio, bạn tạo một **Web Service Request** mới với tên `Initialize_Session` trong thư mục `Object Repository` (hoặc tạo file `Initialize_Session.rs` trong folder Object Repository của dự án) với nội dung XML cấu hình như sau:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<WebServiceRequestEntity>
   <description>Khởi tạo phiên phỏng vấn thành công</description>
   <name>Initialize_Session</name>
   <tag></tag>
   <elementGuidId>a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d</elementGuidId>
   <selectorMethod>BASIC</selectorMethod>
   <smartLocatorEnabled>false</smartLocatorEnabled>
   <useRalativeImagePath>false</useRalativeImagePath>
   <connectionTimeout>-1</connectionTimeout>
   <followRedirects>false</followRedirects>
   <httpBody>{
  "cv_id": "${cvId}",
  "job_title": "Python/FastAPI Backend Developer",
  "jd_text": "Chúng tôi đang tìm kiếm lập trình viên Python phát triển API sử dụng FastAPI. Yêu cầu ít nhất 2 năm kinh nghiệm làm việc.",
  "mode": "practice",
  "duration_minutes": 5
}</httpBody>
   <httpBodyType>text</httpBodyType>
   <httpHeaderProperties>
      <isSelected>true</isSelected>
      <matchCondition>equals</matchCondition>
      <name>Content-Type</name>
      <type>Main</type>
      <value>application/json</value>
   </httpHeaderProperties>
   <httpHeaderProperties>
      <isSelected>true</isSelected>
      <matchCondition>equals</matchCondition>
      <name>Authorization</name>
      <type>Main</type>
      <value>Bearer ${authToken}</value>
   </httpHeaderProperties>
   <katalonVersion>9.0.0</katalonVersion>
   <maxResponseSize>-1</maxResponseSize>
   <migratedVersion>5.4.1</migratedVersion>
   <restRequestMethod>POST</restRequestMethod>
   <restUrl>${baseUrl}/api/v1/interview/sessions</restUrl>
   <serviceType>RESTful</serviceType>
   <soapBody></soapBody>
   <soapHeader></soapHeader>
   <soapRequestMethod></soapRequestMethod>
   <soapServiceEndpoint></soapServiceEndpoint>
   <soapServiceFunction></soapServiceFunction>
   <socketTimeout>-1</socketTimeout>
   <useServiceInfoFromWsdl>false</useServiceInfoFromWsdl>
   <variables>
      <defaultValue>'http://178.128.37.124:8000'</defaultValue>
      <description>IP và Cổng chạy backend</description>
      <id>1</id>
      <masked>false</masked>
      <name>baseUrl</name>
   </variables>
   <variables>
      <defaultValue>''</defaultValue>
      <description>Token xác thực lấy từ API login</description>
      <id>2</id>
      <masked>false</masked>
      <name>authToken</name>
   </variables>
   <variables>
      <defaultValue>''</defaultValue>
      <description>Mã CV đã được tải lên từ use case trước</description>
      <id>3</id>
      <masked>false</masked>
      <name>cvId</name>
   </variables>
   <verificationScript>import static org.assertj.core.api.Assertions.*
import com.kms.katalon.core.testobject.ResponseObject
import com.kms.katalon.core.webservice.keyword.WSBuiltInKeywords as WS

ResponseObject response = WSResponseManager.getInstance().getCurrentResponse()</verificationScript>
   <wsdlAddress></wsdlAddress>
</WebServiceRequestEntity>
```

---

## 2. Viết Test Case Script (Groovy Code)
Để lấy **Access Token** và **CV ID** điền vào script kiểm thử, bạn có thể thực hiện theo các cách đơn giản sau:

---

### 1. Cách lấy Access Token (JWT Token)

#### **Cách 1: Lấy trực tiếp từ trình duyệt (Nhanh nhất)**
1. Mở trang web LancerAI của bạn trên Chrome/Edge và tiến hành **Đăng nhập**.
2. Nhấn phím **`F12`** để mở bộ công cụ nhà phát triển (DevTools).
3. Chuyển sang tab **`Application`** (trên Chrome) hoặc **`Storage`** (trên Firefox/Safari).
4. Ở cột bên trái, tìm mục **`Local Storage`** và click vào địa chỉ trang web của bạn (ví dụ: `http://178.128.37.124` hoặc `http://localhost:3000`).
5. Ở bảng bên phải, tìm khóa (Key) tên là **`token`** hoặc **`user`**. Giá trị (Value) của nó chính là mã JWT của bạn (một chuỗi rất dài bắt đầu bằng `eyJhbGciOi...`). Hãy copy toàn bộ chuỗi đó.

#### **Cách 2: Gửi request đăng nhập qua Postman/Katalon**
Gửi một request `POST` tới: `http://178.128.37.124:8000/api/v1/auth/login` với nội dung Body JSON:
```json
{
  "email": "email_tai_khoan_cua_ban@example.com",
  "password": "mat_khau_cua_ban"
}
```
Kết quả trả về sẽ có dạng:
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```
Bạn chỉ cần lấy giá trị của `"access_token"`.

---

### 2. Cách lấy CV ID

#### **Cách 1: Lấy từ thanh địa chỉ URL của trình duyệt (Nhanh nhất)**
1. Đăng nhập vào trang web, truy cập vào màn hình **Tối ưu hóa CV** (CV Optimization) và nhấn chọn xem CV của bạn.
2. Nhìn lên thanh địa chỉ của trình duyệt, URL sẽ có dạng:
   `http://178.128.37.124/optimization/cvs/550e8400-e29b-41d4-a716-446655440000`
3. Chuỗi ký tự ở cuối cùng chính là **CV ID** (Ví dụ ở đây là: `550e8400-e29b-41d4-a716-446655440000`).

#### **Cách 2: Gọi API lấy danh sách CV**
Gửi một request `GET` tới: `http://178.128.37.124:8000/api/v1/optimization/cvs`
*(Lưu ý: Phải truyền Header `Authorization: Bearer <Access Token lấy được ở bước 1>`)*.

Kết quả trả về là danh sách các CV dạng JSON:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "CV_PhamNgocDuy.pdf",
    "created_at": "2026-07-09T10:00:00Z"
  }
]
```
Bạn copy chuỗi trong trường `"id"` làm `cvId` để chạy test.


Sau đó bạn tạo một **Test Case** mới trong Katalon Studio với tên `TC01_Initialize_Interview_Session` và chuyển sang chế độ **Script Mode** rồi copy đoạn code dưới đây vào:
```groovy
import static com.kms.katalon.core.testobject.ObjectRepository.findTestObject
import com.kms.katalon.core.webservice.keyword.WSBuiltInKeywords as WS
import com.kms.katalon.core.model.FailureHandling as FailureHandling
import groovy.json.JsonSlurper as JsonSlurper
import com.kms.katalon.core.util.KeywordUtil as KeywordUtil

// 1. Cấu hình các thông tin biến môi trường kiểm thử
String baseUrl   = "http://178.128.37.124:8000"
String authToken = "YOUR_ACCESS_TOKEN_HERE" // Điền JWT Token của ứng viên đã đăng nhập
String cvId      = "YOUR_CV_ID_HERE"      // Điền mã ID của CV đã upload thành công trước đó

KeywordUtil.logInfo("Bắt đầu gửi yêu cầu tạo phiên phỏng vấn...")

// 2. Gửi yêu cầu POST tới API /sessions thông qua Test Object
def response = WS.sendRequest(findTestObject('Object Repository/Initialize_Session', [
    'baseUrl'   : baseUrl,
    'authToken' : authToken,
    'cvId'      : cvId
]))

// 3. Kiểm tra mã trạng thái phản hồi mong muốn (201 Created)
WS.verifyResponseStatusCode(response, 201)
KeywordUtil.logInfo("API phản hồi mã trạng thái 201 - Thành công.")

// 4. Giải mã (parse) dữ liệu JSON nhận được từ Response Body
def jsonResponse = new JsonSlurper().parseText(response.getResponseBodyContent())

// 5. Xác thực (Assertion) cấu trúc dữ liệu trả về
String sessionId = jsonResponse.session_id
KeywordUtil.logInfo("Nhận được Session ID mới: " + sessionId)

// Xác thực: session_id không được null và phải là chuỗi có độ dài lớn hơn 0
assert sessionId != null : "LỖI: API không trả về session_id!"
assert sessionId.trim().length() > 0 : "LỖI: session_id trống!"

// Xác thực thêm các trường cơ bản khác nếu cần thiết
assert jsonResponse.user_id != null : "LỖI: Không tìm thấy trường user_id!"
assert jsonResponse.status == "incomplete" : "LỖI: Phiên mới tạo phải có trạng thái mặc định là 'incomplete'!"

KeywordUtil.markPassed("PASSED: Khởi tạo phiên phỏng vấn thành công. Session ID: " + sessionId)
```

---

## 3. Cách tester thực hiện trong Katalon Studio:
1.  **Bước 1:** Sao chép nội dung phần **1** tạo thành file `Initialize_Session.rs` lưu trong thư mục `Object Repository/` của dự án Katalon.
2.  **Bước 2:** Tạo một Test Case mới, dán đoạn mã Groovy ở phần **2** vào mục Script.
3.  **Bước 3:** Chạy thử Test Case (Run) để kiểm tra, kết quả log sẽ hiển thị `PASSED` và in ra `session_id` được sinh ra tự động từ server LancerAI.
