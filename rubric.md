# Thang chấm lab S2

Tổng 100 điểm, quy về 3 phần trăm điểm học phần. Máy chấm 60, người chấm 30, phần tái lập 10.

| Tiêu chí | Trọng số | Ai chấm | Tốt, 100% | Khá, 75% | Trung bình, 50% | Kém, 0% |
|---|---|---|---|---|---|---|
| Bộ kiểm tự động | 60 | Máy | Mười sáu phép kiểm xanh | Một tới hai phép đỏ | Ba tới năm phép đỏ | Từ sáu phép đỏ trở lên, hoặc không nộp |
| Cột thứ ba của bảng: thứ vẫn còn qua được | 12 | Người | Mỗi dòng nêu một đường vào còn lại, cụ thể tới mức nói được kẻ tấn công đứng ở đâu và với quyền gì, và ít nhất một dòng chỉ ra chỗ chính biện pháp vừa dựng mở ra | Đa số dòng nêu được đường vào còn lại, một hai dòng còn chung chung | Khoảng một nửa số dòng để trống hoặc chỉ ghi rằng không còn gì qua được | Bỏ trống, hoặc viết rằng hệ thống đã an toàn sau khi vá |
| Cột thứ hai của bảng: chi phí vận hành | 8 | Người | Mỗi biện pháp quy được ra thao tác thủ công mỗi tuần, có đơn vị, và có căn cứ ước lượng | Có đơn vị nhưng căn cứ mơ hồ | Chỉ ghi nặng hay nhẹ, không quy ra được | Không có, hoặc ghi rằng không ảnh hưởng gì cho mọi dòng |
| Đọc chỉ số Lynis đúng bản chất | 6 | Người | Nói được Lynis nhìn thấy thay đổi nào và không nhìn thấy thay đổi nào, và không coi chỉ số là đại lượng cần tối ưu | Nhận ra chỉ số là đại lượng thay thế nhưng không chỉ ra được phần nó bỏ sót | Chỉ thuật lại con số tăng hay giảm | Bật thêm tùy chọn không liên quan để đẩy chỉ số lên, hoặc giải thích sai bản chất |
| Biện pháp đã cân nhắc rồi bỏ | 4 | Người | Nêu một biện pháp cụ thể, nói rõ nó cắt được rủi ro nào và vì sao phần cắt được không bù nổi chi phí | Có nêu nhưng lý do bỏ chỉ dừng ở mức khó làm | Nêu một biện pháp không liên quan tới bài | Không có |
| Tái lập được | 10 | Máy | `make verify` xanh trên kho sạch mới nhân bản, sau khi chạy đúng chuỗi lệnh ghi trong README, không thao tác tay nào ngoài chuỗi ấy | Cần đúng một thao tác tay không ghi trong README | Cần nhiều thao tác tay | Không chạy được |

## Hai điều người chấm không trừ điểm

**Chỉ số Lynis không tăng, hoặc tụt.** Lynis quét hệ tệp bên trong ảnh nên nó mù với ba biện pháp nặng nhất của bài, là bỏ năng lực, chặn leo quyền qua setuid, và hệ tệp chỉ đọc. Một bài làm đúng cả ba mà chỉ số đứng yên là chuyện bình thường, và giải thích được khoảng cách ấy thì ăn trọn điểm tiêu chí thứ tư. Điều bị trừ là đẩy chỉ số lên bằng cách bật hàng loạt tùy chọn mà dịch vụ không dùng, tức tối ưu đại lượng thay thế thay vì giảm rủi ro thật.

**Chọn giữ cổng 80 hay đổi sang cổng không đặc quyền.** Hai đường đều đúng nếu bạn nói được vì sao. Giữ cổng 80 thì phải cấp lại một năng lực và phải bảo vệ được lựa chọn ấy; đổi cổng thì phải sửa cả tệp cấu hình lẫn ánh xạ cổng và phải nói được ai chịu ảnh hưởng. Bài này đo chất lượng lập luận về đánh đổi, không đo việc bạn đoán trúng đáp án mà người ra đề nghĩ trong đầu.

## Một điều bị trừ nặng

**Khai một con số mà tệp bằng chứng không đỡ lưng.** Bộ kiểm đối chiếu từng con số trong `docs/do-luong.yaml` với tệp tương ứng trong `evidence/S02`, nên chuyện này bị máy bắt trước. Khi bị bắt, nó không được xử như một lỗi gõ nhầm: bài rơi thẳng xuống mức Kém của tiêu chí thứ hai và thứ ba, kể cả khi các phép kiểm còn lại xanh.

Lý do nằm ở chính nghề này. Cả buổi học dựng quanh một chuyển động, từ một câu tự nhận là đã an toàn sang một con số đo được, mà một con số không có bằng chứng đỡ lưng thì lại đúng là câu tự nhận ấy, chỉ khoác thêm vẻ chính xác. Trong một báo cáo an toàn thật, đó là loại lỗi làm hỏng niềm tin vào toàn bộ phần còn lại của báo cáo.
