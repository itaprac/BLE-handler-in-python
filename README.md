# Opis aplikacji BLE 

## Co robi ten kod
1. Skanuje dostępne urządzenia BLE.
2. Łączy się z wybranym urządzeniem.
3. Wysyła do niego wiadomości.
4. Rozłącza się** po zakończeniu.

Wszystko zrobione w klasie `BleHandler`, która obsługuje cały proces. 

## Importy

```python
import asyncio
from bleak import BleakClient, BleakScanner
```

- **BleakClient i BleakScanner**: Potrzebne do obsługi urządzeń BLE
- **asyncio**: Wymagane przez `bleak` do asynchronicznej pracy. Asynchroniczność też jest tutaj przydatna jakbyśmy chcieli np. dodać odbieranie wiadomości, i chcemy żeby to działało "równocześnie" z wysyłaniem.

## Ustawiamy Stałe UUID

```python
SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
CHARACTERISTIC_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
```

SERVICE_UUID i CHARACTERISTIC_UUID, ustawiane jako stałe (może lepiej ustawiać je w mainie? sam nie wiem.) Może głupio to wygląda że pod nimi jest klasa, ale zakładam że klasa i tak by była w innym pliku jeżeli rzeczywiście była by skończona i używana.

## Klasa `BleHandler` 
### Inicjalizacja

```python
class BleHandler:
    def __init__(self, device_name, service_uuid=SERVICE_UUID, characteristic_uuid=CHARACTERISTIC_UUID):
        self.device_name = device_name
        self.service_uuid = service_uuid
        self.characteristic_uuid = characteristic_uuid
        self.client = None
        self.target_device = None
```

- **device_name**: Nazwa urządzenia, z którym chcemy się połączyć.
- **service_uuid & characteristic_uuid**: UUID usługi i charakterystyki.
- **client & target_device**: Miejsca, gdzie przechowujemy klienta BLE i docelowe urządzenie.

### Skanowanie Urządzeń

```python
async def scan(self, timeout: float = 5.0) -> bool:
    scanner = BleakScanner()
    devices = []
    print(f"Skanowanie urządzeń BLE przez {timeout} sekund")
    try:
        devices = await scanner.discover(timeout=timeout)
        for device in devices:
            if device.name == self.device_name:
                self.target_device = device
                print(f"Znaleziono urządzenie: {device.name}, adres: {device.address}")
                return True
        print(f"Nie znaleziono urządzenia o nazwie {self.device_name}")
        return False
    except Exception as e:
        print(f"Nie udało się zeskanować urządzeń: {e}")
        return False
```

- **BleakScanner()**: Skanuje urządzenia w zasięgu.
- **Timeout**: Czas trwania skanowania – domyślnie 5 sekund.
- **scanner.discover()**: Zwraca listę urządzeń w zasięgu.
- **Pętla for**: Szukanie urządzenia o podanej nazwie i zapisanie go do `target_device`.

### Łączenie z Urządzeniem

```python
    async def connect(self) -> bool:
        if not self.target_device:
            print("Brak urządzenia")
            return False

        try:
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
```

- **BleakClient**: Tworzymy klienta BLE dla naszego urządzenia.
- **client.connect()**: Próba połączenia z urządzeniem.

### Wysyłanie Wiadomości

```python
    async def send_message(self, message: str = "test", count: int = 10, delay: int = 3) -> bool:
        if not self.client or not self.client.is_connected:
            print("Brak połączenia z urządzeniem")
            return False

        # while True:
        for i in range(count):
            try:
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
```

- **Pętla**: Tutaj w praktyce pewnie, pętla `while True` byłaby lepsza, bo zakładam, że robot ma mieć możliwość ciągłej komunikacji z urządzeniem, ale dla testów zostawiłem pętlę for.
- **message, count, delay**: Wiadomość, liczba wysłań i opóźnienie między nimi.
- **write_gatt_char**: Wysyłamy wiadomość do urządzenia.
- **await asyncio.sleep()**: Czekanie przez `delay` sekund między wysyłkami.

### Rozłączanie z Urządzeniem

```python
    async def disconnect(self) -> bool:
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print(f"Rozłączono z urządzeniem {self.device_name}")
            return True
        else:
            print(f"Brak połączenia z urządzeniem {self.device_name}")
            return False
```

- **client.disconnect()**: Rozłączenie z urządzeniem, jeśli jest połączone.

### Uruchamianie Całego Procesu

```python
    async def run(self, message: str = "test", count: int = 10, delay: int = 3, scan_timout: float = 5.0) -> bool:
        try:
            if not await self.scan(scan_timout):
                return False

            if not await self.connect():
                return False

            if not await self.send_message(message, count, delay):
                return False

        finally:
            await self.disconnect()
        return True
```

- Tutaj łączymy wszystkie kroki w jedną funkcję `run()`. 
- **finally**: Rozłączamy się z urządzeniem, nawet jeśli wystąpił błąd / wyjątek.

## Main

```python
async def main():
    nazwa = "Robokot"
    wiadomosc = "aaa"
    liczba_wiadom = 10
    opoznienie = 3

    ble_handler = BleHandler(device_name=nazwa)
    await ble_handler.run(message=wiadomosc, count=liczba_wiadom, delay=opoznienie)
```

- Prosty main, gdzie ustawiamy nazwę urządzenia, wiadomość, liczbę wysłań i opóźnienie.
- **BleHandler**: Tworzymy instancję klasy i uruchamiamy cały proces.

### Uruchomienie 

```python
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrzerwano")
```

- **asyncio.run()**: Uruchamia maina (tworzy `event loop`).
- **KeyboardInterrupt**: Taki dodatek żeby przy stopowaniu programu przy użyciu `Ctrl+c` nie było błędów.

### Moje sugestie na przyszłość (jeżeli to ma jakąś przyszłość xd)

- **Odbieranie wiadomości**: Można dodać prosta metodę do odbierania wiadomości z urządzenia.
- **GUI?**: Spoko sprawa, ale robilem raz GUI w Pythonie i troche z tym roboty, a nie wiem czy to jest potrzebne. 
- **Logowanie**: Jakby to rzeczywiście miało działać na robocie, to warto by było dodać logowanie do pliku, albo wysyłanie logów na serwer czy coś takiego.

### PS:
Pierwszy raz robiłem coś z BLE, i nie zagłębiałem się bardzo w szczegóły jak to działa, bardziej skupiłem się na bibliotece bleak i jak to po prostu zaimplementować. Tak samo pierwszy raz (chyba) robiłem coś asynchronicznego więc nie jestem pewien czy to jest najlepsze rozwiązanie, ale działa. 
I wiem, że trochę jest mieszanina polskiego i angielskiego, ale zmienne w klasach po angielsku sa jakos dla mnie bardziej intuicyjne, a komentarze i printy po polsku są bardziej zrozumiałe.

---

- [Dokumentacja Bleak](https://bleak.readthedocs.io/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

