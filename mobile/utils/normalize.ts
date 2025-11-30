export function toBool(x: any) {
  return x === true || x === "true";
}

export function toNum(x: any, fallback = 1) {
  const n = Number(x);
  return isNaN(n) ? fallback : n;
}
