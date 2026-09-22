/* Chương trình phụ trợ đọc tệp bí mật của dịch vụ.
 *
 * Trong ảnh khởi đầu, tệp nhị phân này mang bit setuid và thuộc sở hữu root, nên
 * người gọi nào cũng đọc được tệp mà quyền tệp vốn chỉ cho root đọc. Đó là kỹ
 * thuật T1548.001 của ATT&CK (phiên bản 19.2), và phần phòng thủ của bài phải chặn
 * nó. Chương trình không nhận đối số và không mở đường chạy lệnh nào, nên nó chỉ
 * chứng minh một điều: bit setuid đang có hiệu lực hay đã hết hiệu lực.
 *
 * Mỗi lần chạy, chương trình ghi một dòng vào nhật ký của dịch vụ, gồm cả uid thật
 * và uid hiệu dụng. Hai số khác nhau nghĩa là tiến trình đang chạy với quyền của chủ
 * tệp chứ không phải quyền của người gọi. Trên một máy thật, việc ghi lại điều này
 * do auditd đảm nhận; trong lab, auditd không chạy được bên trong container nên
 * chương trình tự ghi. Buổi S7 sẽ tìm lại chính dòng này trong nhật ký của bạn,
 * nên khuôn dòng giữ đúng khuôn của dịch vụ: thời điểm, su_kien, uid, euid, chi_tiet.
 */
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#ifndef TEP_BI_MAT
#define TEP_BI_MAT "/etc/css-s02/bi-mat.txt"
#endif
#ifndef TEP_NHAT_KY
#define TEP_NHAT_KY "/var/log/css-s02/dich-vu.log"
#endif

/* Mở tệp nhật ký ở chế độ ghi nối tiếp và KHÔNG tạo tệp mới. Dịch vụ đã tạo tệp
 * lúc khởi động; nếu chương trình này tạo trước, tệp sẽ thuộc về root, và dịch vụ
 * sau khi làm cứng (chạy dưới sv) không ghi tiếp được nữa. */
static void ghi_nhat_ky(const char *su_kien, const char *chi_tiet)
{
    int fd = open(TEP_NHAT_KY, O_WRONLY | O_APPEND);
    if (fd < 0) {
        return;
    }
    char thoi_diem[40];
    time_t bay_gio = time(NULL);
    strftime(thoi_diem, sizeof thoi_diem, "%Y-%m-%dT%H:%M:%S%z", localtime(&bay_gio));
    char dong[512];
    int n = snprintf(dong, sizeof dong, "%s su_kien=%s uid=%d euid=%d chi_tiet=%s\n",
                     thoi_diem, su_kien, (int)getuid(), (int)geteuid(), chi_tiet);
    if (n > 0) {
        size_t dai = (size_t)n < sizeof dong ? (size_t)n : sizeof dong - 1;
        (void)!write(fd, dong, dai);
    }
    close(fd);
}

int main(void)
{
    if (geteuid() != getuid()) {
        ghi_nhat_ky("leo_quyen", "doc-bimat chay voi uid hieu dung cua chu tep qua bit setuid");
    }

    FILE *f = fopen(TEP_BI_MAT, "r");
    if (f == NULL) {
        ghi_nhat_ky("tu_choi", "doc-bimat khong mo duoc " TEP_BI_MAT);
        perror("doc-bimat");
        return 1;
    }

    char dong[256];
    while (fgets(dong, sizeof dong, f) != NULL) {
        fputs(dong, stdout);
    }
    fclose(f);
    return 0;
}
