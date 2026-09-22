/* Sáu dòng C của mục 2.5 giáo trình, dựng lại thành một chương trình chạy được.
 *
 * Một biến điều khiển luồng nằm ngay cạnh một vùng đệm, và một phép chép chuỗi
 * không kiểm biên đi qua ranh giới giữa hai thứ. Không dòng nào gán cho da_duyet,
 * nhưng dữ liệu đầu vào đổi được giá trị của nó. Trong CWE 4.20 đây là CWE-787.
 *
 * Chương trình trả về 7 khi luồng điều khiển đã bị dữ liệu đầu vào lái, và trả về
 * 0 khi không. Mã thoát là thứ bộ kiểm đọc, vì nó là quan sát khách quan duy nhất
 * mà máy lấy được từ thí nghiệm này.
 */
#include <stdio.h>
#include <string.h>

static int ghi_ten(const char *nguon)
{
    int  da_duyet = 0;
    char ten[16];

    strcpy(ten, nguon);          /* không ai kiểm độ dài của nguon */
    printf("ten=%s da_duyet=%d\n", ten, da_duyet);
    return da_duyet;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "dung: ghi-ten <chuoi>\n");
        return 2;
    }
    return ghi_ten(argv[1]) ? 7 : 0;
}
