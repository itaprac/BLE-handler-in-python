import asyncio

from bleak import BleakClient, BleakScanner

SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
CHARACTERISTIC_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"


# Klasa obsługująca BLE
class BleHandler:
    # Konstruktor
    def __init__(
        self,
        device_name,
        service_uuid=SERVICE_UUID,
        characteristic_uuid=CHARACTERISTIC_UUID,
    ):
        self.device_name = device_name
        self.service_uuid = service_uuid
        self.characteristic_uuid = characteristic_uuid
        self.client = None
        self.target_device = None

    # Metoda skanująca urządzenia
    async def scan(self, timeout: float = 5.0) -> bool:
        """
        Skanuje urządzenia BLE w poszukiwaniu urządzenia o nazwie self.device_name
        """
        # Utworzenie skanera
        scanner = BleakScanner()
        devices = []
        print(f"Skanowanie urządzeń BLE przez {timeout} sekund")
        try:
            # Skanowanie urządzeń
            devices = await scanner.discover(timeout=timeout)
            # Wyszukanie urządzenia o nazwie self.device_name i zapisanie go w self.target_device
            for device in devices:
                if device.name == self.device_name:
                    self.target_device = device
                    print(
                        f"Znaleziono urządzenie: {device.name}, adres: {device.address}"
                    )
                    return True
            # W przypadku braku urządzenia
            print(f"Nie znaleziono urządzenia o nazwie {self.device_name}")
            return False
        # W przypadku błędu
        except Exception as e:
            print(f"Nie udało się zeskanować urządzeń: {e}")
            return False

    # Metoda łącząca się z urządzeniem
    async def connect(self) -> bool:
        """
        Łączy się z urządzeniem self.target_device
        """
        # Sprawdzenie czy urządzenie zostało znalezione
        if not self.target_device:
            print("Brak urządzenia")
            return False

        try:
            # Utworzenie klienta i próba połączenia
            self.client = BleakClient(self.target_device)
            await self.client.connect()
            if self.client.is_connected:
                print(f"Połączono z urządzeniem {self.device_name}")
                return True
            else:
                print(f"Nie udało się połączyć z urządzeniem {self.device_name}")
                return False

        except Exception as e:
            print(f"Błąd podczas łączenia z urządzeniem: {e}")
            return False

    # Metoda rozłączająca się z urządzeniem
    async def disconnect(self) -> bool:
        """
        Rozłącza się z urządzeniem
        """
        # Sprawdzenie czy klient jest połączony i próba rozłączenia
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print(f"Rozłączono z urządzeniem {self.device_name}")
            return True
        else:
            print(f"Brak połączenia z urządzeniem {self.device_name}")
            return False

    # Metoda wysyłająca wiadomość
    async def send_message(
        self, message: str = "test", count: int = 10, delay: int = 3
    ) -> bool:
        """
        Wysyła wiadomość message do urządzenia 'count' razy z opóźnieniem 'delay' sekund
        """
        # Sprawdzenie czy klient jest połączony
        if not self.client or not self.client.is_connected:
            print("Brak połączenia z urządzeniem")
            return False

        # Pętla wysyłająca wiadomość (ustawiona jako pętla for dla testów)
        # while True:
        for i in range(count):
            try:
                # Wysłanie wiadomości
                await self.client.write_gatt_char(
                    self.characteristic_uuid, (message + "\n").encode()
                )
                print(f"Wysłano: {message}")

            except Exception as e:
                print(f"Błąd podczas wysyłania wiadomości: {e}")
                break

            # Oczekiwanie 'delay' sekund (w ostatniej iteracji nie czeka) - dla testów, uzywać drugiej lini z while
            await asyncio.sleep(delay) if i < count - 1 else None
            # await asyncio.sleep(delay)

        print(f"Wysyłanie wiadomości zakończone")
        return True

    # Metoda uruchamiająca cały proces
    async def run(
        self,
        message: str = "test",
        count: int = 10,
        delay: int = 3,
        scan_timout: float = 5.0,
    ) -> bool:
        """
        Uruchamia cały proces: skanowanie, łączenie, wysyłanie wiadomości, rozłączanie
        """
        try:
            # Skanowanie, łączenie, wysyłanie wiadomości
            if not await self.scan(scan_timout):
                return False

            if not await self.connect():
                return False

            if not await self.send_message(message, count, delay):
                return False

        # Rozłączanie (nawet jeśli wystąpi błąd)
        finally:
            await self.disconnect()
        return True


async def main():
    # Ustawienia
    nazwa = "Robokot"
    wiadomosc = "aaa"
    liczba_wiadom = 10
    opoznienie = 3

    # Tworzenie obiektu / instancji klasy BleHandler i uruchomienie procesu
    ble_handler = BleHandler(device_name=nazwa)
    await ble_handler.run(message=wiadomosc, count=liczba_wiadom, delay=opoznienie)


if __name__ == "__main__":
    try:
        # Uruchomienie maina (inicjalizacja event loop z asyncio)
        asyncio.run(main())
    # Dodatkowy wyjątek przechwytujący przerwanie klawiszem Ctrl+C, aby program nie kończył się błędem
    except KeyboardInterrupt:
        print("\nPrzerwano")
