#!/usr/bin/env python3
# 控制 ESP32-C3 CursorLight BLE 状态灯
#
# 首次安装：
#   python3 -m pip install bleak
#
# 用法：
#   python3 cursor_light_ble_enhanced.py demo
#   python3 cursor_light_ble_enhanced.py thinking
#   ...
#
# Dry-run（无硬件测试）：
#   CURSOR_LIGHT_DRY_RUN=1 python3 cursor_light_ble_enhanced.py thinking

import os
import sys

DEVICE_NAME = "CursorLight"
MODE_CHAR_UUID = "b8b7e002-7a6b-4f4f-9a8b-11c0ffee0001"

VALID_MODES = {
    "red",
    "yellow",
    "green",
    "busy",
    "error",
    "thinking",
    "ai",
    "success",
    "traffic",
    "alarm",
    "demo",
    "off",
}

DRY_RUN = os.environ.get("CURSOR_LIGHT_DRY_RUN", "").strip() in ("1", "true", "yes")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 cursor_light_ble_enhanced.py <mode>")
        print("可用 mode:", ", ".join(sorted(VALID_MODES)))
        sys.exit(1)

    mode = sys.argv[1].strip().lower()
    if mode not in VALID_MODES:
        print(f"未知 mode: {mode}")
        print("可用 mode:", ", ".join(sorted(VALID_MODES)))
        sys.exit(1)

    if DRY_RUN:
        print(f"[dry-run] mode={mode}")
        return

    import asyncio
    from bleak import BleakScanner, BleakClient

    async def ble_send():
        print(f"正在扫描 BLE 设备：{DEVICE_NAME} ...")
        device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=10.0)

        if device is None:
            print("没有找到 CursorLight。请确认：")
            print("1. ESP32 已通电")
            print("2. 代码已刷入 BLE 增强版")
            print("3. 距离足够近")
            print("4. macOS 蓝牙已打开，并给 Terminal 蓝牙权限")
            sys.exit(2)

        print(f"找到设备: {device.address}")

        async with BleakClient(device) as client:
            if not client.is_connected:
                print("连接失败")
                sys.exit(3)

            print(f"已连接，发送 mode={mode}")
            await client.write_gatt_char(MODE_CHAR_UUID, mode.encode("utf-8"), response=True)
            print("发送完成")

    asyncio.run(ble_send())


if __name__ == "__main__":
    main()

