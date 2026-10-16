// Se corre con `bun test` desde frontend/.
import { describe, expect, test } from "bun:test";
import { DISPOSITIVOS, detectarDispositivo } from "../src/lib/instrucciones-carga";

const IPHONE =
  "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1";
const ANDROID = "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Mobile Safari/537.36";
const WINDOWS = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36";
const MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15";

describe("dispositivo detectado", () => {
  test("iPhone, Android y computadora", () => {
    expect(detectarDispositivo(IPHONE)).toBe("iphone");
    expect(detectarDispositivo(ANDROID)).toBe("android");
    expect(detectarDispositivo(WINDOWS)).toBe("computadora");
    expect(detectarDispositivo(MAC, 0)).toBe("computadora");
  });
  test("un iPad nuevo se presenta como Mac con pantalla táctil: usa las instrucciones del iPhone", () => {
    expect(detectarDispositivo(MAC, 5)).toBe("iphone");
  });
  test("sin información, computadora", () => {
    expect(detectarDispositivo(undefined)).toBe("computadora");
    expect(detectarDispositivo("")).toBe("computadora");
  });
  test("las tres pestañas son iPhone, Android y Computadora, en ese orden", () => {
    expect(DISPOSITIVOS.map((d) => d.etiqueta)).toEqual(["iPhone", "Android", "Computadora"]);
  });
});
