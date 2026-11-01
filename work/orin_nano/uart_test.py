import serial
import threading
import queue
import time

class UartTester:
    def __init__(self, port="/dev/ttyACM0", baudrate=115200, timeout=0.5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        
        self.serial_port = None
        self.running = False
        self.msg_queue = queue.Queue()
        self.read_thread = None

    @property
    def is_open(self):
        return self.serial_port is not None and self.serial_port.is_open

    def start(self):
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            # 포트 오픈 후 하드웨어 안정화 및 잔여 버퍼 비우기
            time.sleep(0.1)
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()

            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            print(f"[SYSTEM] 포트 연결 완료: {self.port} ({self.baudrate}bps)")
            return True
        except Exception as e:
            print(f"[ERROR] 포트 열기 실패: {e}")
            return False

    def stop(self):
        # 1. 스레드 정지 플래그를 먼저 내려 루프 탈출 유도
        self.running = False
        
        # 2. 스레드가 루프를 마칠 때까지 대기
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1.0)

        # 3. 안전하게 포트 닫기
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

        print("[SYSTEM] 통신 종료")

    def _put_message(self, msg_type, content):
        """수신 및 에러 메시지를 큐에 적재하고 콘솔 출력"""
        self.msg_queue.put((msg_type, content))
        print(f"[{msg_type}] {content}")

    def _read_loop(self):
        import time

        while self.running and self.is_open:
            try:
                waiting = self.serial_port.in_waiting
                if waiting > 0:
                    raw_data = self.serial_port.read(waiting)
                    # 16진수 바이트 값과 텍스트를 함께 출력
                    hex_str = " ".join(f"{b:02X}" for b in raw_data)
                    msg = raw_data.decode("ascii", errors="replace")
                    self._put_message(
                        "RX", f"[{len(raw_data)}B] HEX: {hex_str} | TXT: {repr(msg)}"
                    )
                else:
                    time.sleep(0.01)

            except (OSError, serial.SerialException) as error:
                if self.running:
                    self._put_message("ERROR", f"UART 수신 오류: {error}")
                break

    def send_command(self, cmd_str):
        """STM32로 개행 문자를 붙여 명령어 전송"""
        if not self.is_open:
            print("[WARN] 포트가 열려있지 않습니다.")
            return

        formatted_cmd = f"{cmd_str}\r\n"
        self.serial_port.write(formatted_cmd.encode("ascii"))
        print(f"[TX] {cmd_str}")


if __name__ == "__main__":
    tester = UartTester(port="/dev/ttyACM0", baudrate=115200)

    if tester.start():
        try:
            # 1. 졸음 부저 제어
            print("\n--- [1] 졸음 부저 테스트 ---")
            tester.send_command("DROWSY_WARN")
            time.sleep(1.0)  

            tester.send_command("DROWSY_OK")
            time.sleep(1.0)

            # 2. 공조 환기 팬 제어
            print("\n--- [2] 졸음 에어컨 제어 테스트 ---")
            tester.send_command("VENT_ON")
            time.sleep(1.0)

            # 3. LED 경고 알림 제어 (센터, 우측, 좌측)
            print("\n--- [3] LED 경고 켜기 테스트 ---")
            tester.send_command("WARN_CENTER")
            time.sleep(0.8)

            tester.send_command("WARN_RIGHT")
            time.sleep(0.8)

            tester.send_command("WARN_LEFT")
            time.sleep(0.8)

            # 4. LED 복구(소등) 제어
            print("\n--- [4] LED 끄기 테스트 ---")
            tester.send_command("CENTOR_OK")
            time.sleep(0.8)

            tester.send_command("RIGHT_OK")
            time.sleep(0.8)

            tester.send_command("LEFT_OK")
            time.sleep(0.8)

            # 5. 창문 & 공기청정기 복합 제어
            print("\n--- [5] 창문 및 공기청정기 제어 테스트 ---")
            tester.send_command("WIN_CLOSE")
            time.sleep(1.0)
                        
            tester.send_command("WIN_OPEN")
            time.sleep(1.0)

            # 6. 미등록 커맨드 (NACK 응답 검증)
            print("\n--- [6] 예외 커맨드 테스트 ---")
            tester.send_command("INVALID_CMD")
            time.sleep(1.0)

        except KeyboardInterrupt:
            print("\n[USER] 사용자에 의해 중단됨")
        finally:
            tester.stop()