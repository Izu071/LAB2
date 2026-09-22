# Lab S2. Mục tiêu theo chuẩn chung của học phần, cộng hai mục tiêu riêng của bài
# là stack-protector và phần đo trước và sau.
#
# Ảnh nền ghim theo digest sau khi chạy ghim-digest.sh. Múi giờ, locale và hạt
# giống cố định để hai lần chạy cho cùng kết quả.

SHELL := /bin/bash
export TZ := Asia/Ho_Chi_Minh
export LC_ALL := C.UTF-8
export PYTHONHASHSEED := 0

EVID := evidence/S02
DC   := docker compose
TRONG_DICH_VU := $(DC) exec -T dichvu
NHU_SV        := $(DC) exec -T -u sv dichvu

.PHONY: preflight up attack defend stack-protector verify export-evidence down help

help:
	@echo "preflight        ghi thông tin máy, kiểm Docker chạy được"
	@echo "up               dựng dịch vụ ở trạng thái khởi đầu, đo lần thứ nhất"
	@echo "attack           chạy phép chứng minh một bước trên trạng thái khởi đầu"
	@echo "                 (sửa docker-compose.yml và dich-vu/Dockerfile ở bước này)"
	@echo "defend           dựng lại theo cấu hình bạn đã sửa, đo lần thứ hai"
	@echo "stack-protector  dịch ghi-ten.c hai lần và ghi lại hai mã thoát"
	@echo "verify           chạy bộ kiểm, đây là thứ bộ chấm chạy"
	@echo "export-evidence  gom bằng chứng và nhật ký vào $(EVID), kèm SHA256SUMS"
	@echo "down             dọn môi trường, giữ lại $(EVID)"

preflight:
	@mkdir -p $(EVID)
	@{ \
	  echo "kien truc CPU: $$(uname -m)"; \
	  echo "he dieu hanh : $$(uname -s)"; \
	  echo "phien ban Python: $$(python3 --version 2>&1)"; \
	  if command -v free >/dev/null 2>&1; then \
	    echo "RAM kha dung: $$(free -m | awk '/^Mem:/ {print $$7 " MiB"}')"; \
	  else \
	    echo "RAM kha dung: KHONG DO DUOC tren he dieu hanh nay"; \
	  fi; \
	  echo "dia trong: $$(df -Pm . | awk 'NR==2 {print $$4 " MiB"}')"; \
	  if command -v docker >/dev/null 2>&1; then \
	    echo "phien ban Docker: $$(docker --version 2>&1)"; \
	    if docker info >/dev/null 2>&1; then \
	      echo "docker daemon: chay"; \
	    else \
	      echo "docker daemon: KHONG CHAY"; \
	    fi; \
	  else \
	    echo "phien ban Docker: KHONG CO"; \
	    echo "docker daemon: KHONG CHAY"; \
	  fi; \
	} > $(EVID)/preflight.txt
	@cat $(EVID)/preflight.txt
	@echo
	@echo "Đã ghi $(EVID)/preflight.txt"

up:
	@mkdir -p $(EVID)
	$(DC) up -d --build
	@echo "Đợi dịch vụ trả lời, tối đa 30 giây."
	@for i in $$(seq 1 30); do \
	  if $(TRONG_DICH_VU) /usr/local/bin/thu-dich-vu.sh 2>/dev/null | grep -q 'ma=[0-9]'; then break; fi; \
	  sleep 1; \
	done
	@if [ -f $(EVID)/capsh-truoc.txt ]; then \
	  echo "Đã có số đo lần thứ nhất, không ghi đè. Muốn đo lại từ đầu thì xóa $(EVID) rồi chạy lại."; \
	else \
	  $(TRONG_DICH_VU) /usr/local/bin/do-nang-luc.sh    > $(EVID)/capsh-truoc.txt; \
	  $(TRONG_DICH_VU) /usr/local/bin/do-quyen-tep.sh   > $(EVID)/quyen-tep-truoc.txt; \
	  $(TRONG_DICH_VU) /usr/local/bin/thu-dich-vu.sh    > $(EVID)/dich-vu-truoc.txt; \
	  $(DC) --profile kiem run --rm --no-deps kiem      > $(EVID)/lynis-truoc.txt; \
	  echo "Đã ghi số đo lần thứ nhất vào $(EVID)."; \
	fi

attack:
	@mkdir -p $(EVID)
	@echo "Hai phép thử chạy dưới người dùng sv, trong container của chính bạn."
	$(NHU_SV) /usr/local/bin/thu-leo-quyen.sh | tee $(EVID)/attack-truoc.txt

defend:
	@mkdir -p $(EVID)
	@echo "Dựng lại theo cấu hình bạn đã sửa. Không có bước nào ở đây làm hộ bạn."
	$(DC) up -d --build --force-recreate
	@for i in $$(seq 1 30); do \
	  if $(TRONG_DICH_VU) /usr/local/bin/thu-dich-vu.sh 2>/dev/null | grep -q 'ma=[0-9]'; then break; fi; \
	  sleep 1; \
	done
	$(TRONG_DICH_VU) /usr/local/bin/do-nang-luc.sh  > $(EVID)/capsh-sau.txt
	$(TRONG_DICH_VU) /usr/local/bin/do-quyen-tep.sh > $(EVID)/quyen-tep.txt
	$(TRONG_DICH_VU) /usr/local/bin/thu-dich-vu.sh  > $(EVID)/dich-vu-sau.txt
	$(DC) --profile kiem run --rm --no-deps kiem    > $(EVID)/lynis-sau.txt
	$(NHU_SV) /usr/local/bin/thu-leo-quyen.sh       > $(EVID)/attack-sau.txt || true
	@echo "Đã ghi số đo lần thứ hai vào $(EVID)."

stack-protector:
	@mkdir -p $(EVID)
	@echo "Thí nghiệm chạy trong container kiểm định, không chạy trong dịch vụ đã"
	@echo "làm cứng, vì trình dịch cần ghi tệp tạm còn hệ tệp gốc của dịch vụ thì"
	@echo "phải ở chế độ chỉ đọc sau khi bạn làm xong phần của mình."
	$(DC) --profile kiem run --rm --no-deps kiem /usr/local/bin/thu-stack-protector.sh \
	  > $(EVID)/stack-protector.txt
	@cat $(EVID)/stack-protector.txt

verify:
	python3 -m pytest tests/ -v --tb=short

export-evidence:
	@mkdir -p $(EVID)
	@$(TRONG_DICH_VU) cat /var/log/css-s02/dich-vu.log > $(EVID)/nhat-ky.txt 2>/dev/null \
	  || echo "KHONG LAY DUOC NHAT KY: container chua chay, chay make defend truoc." > $(EVID)/nhat-ky.txt
	@$(TRONG_DICH_VU) cat /etc/css-s02/phien-ban-goi.txt > $(EVID)/phien-ban-goi.txt 2>/dev/null || true
	@cd $(EVID) && rm -f SHA256SUMS && sha256sum * > SHA256SUMS 2>/dev/null || true
	@echo "Bằng chứng ở $(EVID), kèm SHA256SUMS. Nhật ký ở $(EVID)/nhat-ky.txt là"
	@echo "dữ liệu đầu vào của buổi S7, nên commit nó cùng bài nộp."

down:
	-$(DC) --profile kiem down -v --remove-orphans
