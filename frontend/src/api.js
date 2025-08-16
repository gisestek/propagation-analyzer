export async function uploadFile(file, locator, bin) {
  const formData = new FormData();
  formData.append("locator", locator);
  formData.append("bin_km", bin);
  formData.append("file", file);
  const res = await fetch("/api/analyze", { method: "POST", body: formData });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

