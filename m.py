from aiohttp import ClientResponseError, ClientSession, ClientTimeout
import asyncio, json, os, time
from colorama import Fore, init
from datetime import datetime, timedelta

class MoonRabbits:
    def __init__(self) -> None:
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'id-ID,id;q=0.9',
            'Cache-Control': 'no-cache',
            'Host': 'moonrabbits-api.backersby.com',
            'Origin': 'https://moonrabbits.backersby.com',
            'Pragma': 'no-cache',
            'Referer': 'https://moonrabbits.backersby.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

    def print_message(self, message, color=Fore.WHITE):
        print(f"{color}{message}{Fore.RESET}")

    def print_welcome_message(self):
        print(Fore.LIGHTWHITE_EX + r"""
_  _ _   _ ____ ____ _    ____ _ ____ ___  ____ ____ ___ 
|\ |  \_/  |__| |__/ |    |__| | |__/ |  \ |__/ |  | |__]
| \|   |   |  | |  \ |    |  | | |  \ |__/ |  \ |__| |         
        """)
        print(Fore.LIGHTGREEN_EX + "Nyari Airdrop MoonRabbits")
        print(Fore.LIGHTYELLOW_EX + "Telegram: https://t.me/nyariairdrop")
        print(Fore.RESET)

    async def load_from_txt(self):
        """Memuat cookies dari data.txt file."""
        try:
            with open('data.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            return accounts
        except Exception as e:
            self.print_message(f"Kesalahan saat memuat data.txt: {str(e)}", Fore.LIGHTRED_EX)
            return []

    async def get_account_name(self, cookie: str):
        """Mendapatkan nama akun dari cookie."""
        url = 'https://moonrabbits-api.backersby.com/v1/my-info'
        headers = {**self.headers, 'Cookie': cookie}
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers, ssl=False) as response:
                    response.raise_for_status()
                    account_info = await response.json()
                    return account_info.get('username', 'Tidak diketahui')
        except ClientResponseError as e:
            self.print_message(f"Kesalahan HTTP saat mengambil nama akun: {str(e)}", Fore.LIGHTRED_EX)
            return 'Tidak diketahui'
        except Exception as e:
            self.print_message(f"Kesalahan tak terduga saat mengambil nama akun: {str(e)}", Fore.LIGHTRED_EX)
            return 'Tidak diketahui'

    async def my_mrb(self, cookie: str):
        url = 'https://moonrabbits-api.backersby.com/v1/my-mrb'
        headers = {**self.headers, 'Cookie': cookie}
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers, ssl=False) as response:
                    response.raise_for_status()
                    return await response.json()
        except ClientResponseError as e:
            self.print_message(f"Kesalahan HTTP saat mengambil MRB: {str(e)}", Fore.LIGHTRED_EX)
            return None
        except Exception as e:
            self.print_message(f"Kesalahan tak terduga saat mengambil MRB: {str(e)}", Fore.LIGHTRED_EX)
            return None


    async def my_tasks(self, cookie: str):
        url = 'https://moonrabbits-api.backersby.com/v1/my-tasks'
        headers = {**self.headers, 'Cookie': cookie}
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers, ssl=False) as response:
                    response.raise_for_status()
                    my_tasks = await response.json()
                    for category, tasks in my_tasks.items():
                        for task in tasks:
                            await self.my_tasks_complete(cookie=cookie, task_id=task['id'], task_name=task['name'])
        except ClientResponseError as e:
            self.print_message(f"Kesalahan HTTP saat mengambil tugas: {str(e)}", Fore.LIGHTRED_EX)
        except Exception as e:
            self.print_message(f"Kesalahan tak terduga saat mengambil tugas: {str(e)}", Fore.LIGHTRED_EX)

    async def my_tasks_complete(self, cookie: str, task_id: str, task_name: str):
        url = 'https://moonrabbits-api.backersby.com/v1/my-tasks/complete'
        data = json.dumps({'task_id': task_id})
        headers = {
            **self.headers,
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json',
            'Cookie': cookie
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                    if response.status == 400:
                        error_my_tasks_complete = await response.json()
                        if error_my_tasks_complete['message'].startswith('Not enough friends'):
                            self.print_message(f"Teman tidak cukup untuk menyelesaikan tugas {task_name}", Fore.LIGHTYELLOW_EX)
                        elif error_my_tasks_complete['message'] == 'Already completed task':
                            self.print_message(f"Tugas {task_name} sudah diselesaikan", Fore.LIGHTYELLOW_EX)
                        elif error_my_tasks_complete['message'] == 'Already completed daily task today':
                            self.print_message(f"Tugas harian {task_name} sudah diselesaikan hari ini", Fore.LIGHTYELLOW_EX)
                        elif error_my_tasks_complete['message'] == f'Invalid Task: {task_id}':
                            self.print_message(f"ID tugas tidak valid: {task_id}", Fore.LIGHTYELLOW_EX)
                    else:
                        response.raise_for_status()
                        self.print_message(f"Tugas {task_name} selesai", Fore.LIGHTGREEN_EX)
        except ClientResponseError as e:
            self.print_message(f"Kesalahan HTTP saat menyelesaikan tugas {task_name}: {str(e)}", Fore.LIGHTRED_EX)
        except Exception as e:
            self.print_message(f"Kesalahan tak terduga saat menyelesaikan tugas {task_name}: {str(e)}", Fore.LIGHTRED_EX)

    async def countdown(self, seconds):
        """Menghitung mundur dengan tampilan waktu yang bergerak."""
        end_time = datetime.now() + timedelta(seconds=seconds)
        while datetime.now() < end_time:
            remaining_time = end_time - datetime.now()
            print(f"\rWaktu sebelum mulai ulang: {remaining_time}", end="", flush=True)
            await asyncio.sleep(1)
        print()  # Move to the next line after countdown

    async def main(self):
        self.print_welcome_message()
        accounts = await self.load_from_txt()
        total_accounts = len(accounts)
        
        if not accounts:
            self.print_message("Tidak ada akun ditemukan di data.txt", Fore.LIGHTRED_EX)
            return

        while True:
            try:
                total_balance = 0
                self.print_message(f"Memproses {total_accounts} akun dari data.txt", Fore.LIGHTYELLOW_EX)


                for i, cookie in enumerate(accounts):
                    account_name = await self.get_account_name(cookie)
                    self.print_message(f"Memproses akun [{i + 1}/{total_accounts}] dengan nama: {account_name}", Fore.LIGHTYELLOW_EX)

                    # Jalankan tugas dan MRB untuk akun ini
                    await self.my_tasks(cookie=cookie)
                    my_mrb = await self.my_mrb(cookie=cookie)
                    total_balance += my_mrb['total_mrb'] if my_mrb is not None else 0

                    # Jeda 5 detik sebelum memproses akun berikutnya
                    await asyncio.sleep(5)

                self.print_message(f"Total akun diproses: {total_accounts} | Total saldo MRB: {total_balance}", Fore.LIGHTGREEN_EX)

                # Tampilkan hitung mundur 1 hari (24 jam)
                await self.countdown(86400)  # 86400 detik = 1 hari

                # Restart proses setelah hitung mundur
                os.system('cls' if os.name == 'nt' else 'clear')
            except Exception as e:
                self.print_message(f"Kesalahan: {str(e)}", Fore.LIGHTRED_EX)
                continue  # Lanjutkan ke iterasi berikutnya jika terjadi kesalahan


if __name__ == '__main__':
    try:
        init(autoreset=True)
        moonrabbits = MoonRabbits()
        asyncio.run(moonrabbits.main())
    except KeyboardInterrupt:
        print("Keluar...")
