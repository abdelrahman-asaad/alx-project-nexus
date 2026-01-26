
// 🔹 جلب الـ headers مع توكن
function getAuthHeader() {
  const token = localStorage.getItem("access");
  return token ? { "Authorization": `Bearer ${token}` } : {};
}

// 🔹 تسجيل خروج
function logout() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
 window.location.href = `${window.location.origin}/accounts/login/`;}
if (!localStorage.getItem("access")) {
  window.location.href = "/accounts/login/";
}


// 🔹 تحقق من وجود توكن
function checkAuth() {
  const token = localStorage.getItem("access");
  if (!token) logout();
}

// 🔹 دالة fetch مع التحقق وتجديد التوكن تلقائيًا
async function authFetch(url, options = {}) {
  checkAuth();

  // دمج headers مع Authorization
  options.headers = {
    ...options.headers,
    ...getAuthHeader()
  };

  let res = await fetch(url, options);

  // لو انتهت صلاحية التوكن (401) وجربنا التجديد
  if (res.status === 401) {
    const refresh = localStorage.getItem("refresh");
    if (!refresh) {
      logout();
      return;
    }

    // جرب تجديد التوكن
    const tokenRes = await fetch("/api/accounts/token/refresh/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh })
    });

    if (tokenRes.ok) {
      const data = await tokenRes.json();
      localStorage.setItem("access", data.access);

      // إعادة المحاولة للـ request الأصلي
      options.headers = {
        ...options.headers,
        "Authorization": `Bearer ${data.access}`
      };
      res = await fetch(url, options);
    } else {
      logout();
    }
  }

  return res;
}
