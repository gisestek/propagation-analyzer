export async function uploadFile(file, locator, bin) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("locator", locator);
  formData.append("bin_km", bin);

  const res = await fetch("/api/analyze", {
    method: "POST",
    body: formData
  });

  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}
