const API_BASE_URL = "http://127.0.0.1:8000/api"; // Adjust if your API is running on a different port/host

// Helper function to make requests
async function makeRequest(url, method, body = null, headers = {}) {
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
                ...headers
            },
            body: body ? JSON.stringify(body) : null
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || response.statusText);
        }
        return await response.json();
    } catch (error) {
        console.error("Error:", error);
        alert(`Error: ${error.message}`);
        throw error; // Re-throw to be caught by specific form handlers if needed
    }
}

// --- User Authentication ---
document.getElementById("registerForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const userData = {
        email: formData.get("registerEmail"),
        password: formData.get("registerPassword"),
        role: formData.get("registerRole")
    };

    try {
        // console.log(`${API_BASE_URL}/register`);
        await makeRequest(`${API_BASE_URL}/register`, "POST", userData);
        alert("Registration successful! Please log in.");
        document.getElementById("registerForm").reset();
    } catch (error) {
        // Error is already handled in makeRequest, but you can add specific logic here if needed
        console.log(error);
    }
});

document.getElementById("loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const loginData = {
        username: formData.get("loginEmail"),
        password: formData.get("loginPassword")
    };

    try {
        const data = await makeRequest(`${API_BASE_URL}/login`, "POST", loginData);
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("token_type", data.token_type);
    
        // Check the user's role and redirect accordingly
        if (data.role === "admin") {
            window.location.href = "/admin"; // Redirect to the admin panel
        } else {
            alert("You are register as beekeeper please register as admin to access the admin panel!!");
        }
    } catch (error) {
        // Error is already handled in makeRequest
    }
    
});

function getAuthHeaders() {
    const token = localStorage.getItem("access_token");
    const tokenType = localStorage.getItem("token_type");
    if (token && tokenType) {
        return {
            "Authorization": `${tokenType} ${token}`
        };
    }
    return {};
}


document.getElementById("addCropForm").addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent the default form submission

    const formData = new FormData(event.target);
    const cropData = {
        name: formData.get("cropName"),
        floweringStart: formData.get("floweringStart"),
        floweringEnd: formData.get("floweringEnd"),
        latitude: parseFloat(formData.get("cropLatitude")),
        longitude: parseFloat(formData.get("cropLongitude")),
        recommendedHiveDensity: parseInt(formData.get("recommendedHiveDensity"))
    };

    try {
        const headers = getAuthHeaders();
        console.log("sjbdfkjsbdfjbsd")
        await makeRequest(`${API_BASE_URL}/crops`, "POST", cropData, headers);
        alert("Crop entry added successfully!");
        document.getElementById("addCropForm").reset();
    } catch (error) {
        // Error is already handled in makeRequest
    }
});

// --- Hive Log Management ---
document.getElementById("addHiveForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const hiveData = {
        hiveId: formData.get("hiveId"),
        datePlaced: formData.get("datePlaced"),
        latitude: parseFloat(formData.get("latitude")),
        longitude: parseFloat(formData.get("longitude")),
        numColonies: parseInt(formData.get("numColonies"))
    };

    try {
        const headers = getAuthHeaders();
        await makeRequest(`${API_BASE_URL}/hives`, "POST", hiveData, headers);
        alert("Hive log added successfully!");
        document.getElementById("addHiveForm").reset();
    } catch (error) {
        // Error is already handled in makeRequest
    }
});

async function fetchHiveLogs() {
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;
    let url = `${API_BASE_URL}/hives?page=1&limit=100`; // Basic pagination for now
    if (startDate) url += `&startDate=${startDate}`;
    if (endDate) url += `&endDate=${endDate}`;

    try {
        const headers = getAuthHeaders();
        const hives = await makeRequest(url, "GET", null, headers);
        const container = document.getElementById("hiveLogsContainer");
        container.innerHTML = "<h3>Hive Logs:</h3>";
        if (hives.length > 0) {
            hives.forEach(hive => {
                const logItem = document.createElement("div");
                logItem.classList.add("log-item");
                logItem.innerHTML = `<strong>Hive ID:</strong> ${hive.hiveId}, <strong>Date Placed:</strong> ${hive.datePlaced}, <strong>Lat:</strong> ${hive.latitude}, <strong>Lng:</strong> ${hive.longitude}, <strong>Colonies:</strong> ${hive.numColonies}`;
                container.appendChild(logItem);
            });
        } else {
            container.innerHTML += "<p>No hive logs found.</p>";
        }
    } catch (error) {
        // Error is already handled in makeRequest
    }
}

// --- Crop Management (Admin Only) ---
// document.getElementById("addCropCalendarForm").addEventListener("submit", async (event) => {
//     event.preventDefault();
//     const formData = new FormData(event.target);
//     const cropData = {
//         name: formData.get("cropName"),
//         floweringStart: formData.get("floweringStart"),
//         floweringEnd: formData.get("floweringEnd"),
//         latitude: parseFloat(formData.get("cropLatitude")),
//         longitude: parseFloat(formData.get("cropLongitude")),
//         recommendedHiveDensity: parseInt(formData.get("recommendedHiveDensity"))
//     };

//     console.log(cropData);

//     try {
//         const headers = getAuthHeaders();
//         await makeRequest(`${API_BASE_URL}/crops`, "POST", cropData, headers);
//         alert("Crop entry added successfully!");
//         document.getElementById("addCropForm").reset();
//     } catch (error) {
//         // Error is already handled in makeRequest. Check for 403 in admin.html
//     }
// });




async function exportHivesCSV() {
    const startDate = document.getElementById("exportStartDate").value;
    const endDate = document.getElementById("exportEndDate").value;
    let url = `${API_BASE_URL}/hives/export?limit=100`;
    if (startDate) url += `&startDate=${startDate}`;
    if (endDate) url += `&endDate=${endDate}`;

    try {
        const headers = getAuthHeaders();
        const response = await fetch(url, {
            method: "GET",
            headers: headers
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || response.statusText);
        }

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = "hive_logs.csv";
        document.body.appendChild(a);
        a.click();
        a.remove();
    } catch (error) {
        console.error("Error exporting CSV:", error);
        alert(`Error: ${error.message}`);
    }
}


async function fetchNearbyCrops() {
    const latitude = document.getElementById("currentLatitude").value;
    const longitude = document.getElementById("currentLongitude").value;
    const radius = document.getElementById("radius").value;
    const date = document.getElementById("searchDate").value;

    let url = `${API_BASE_URL}/crops/nearby?latitude=${latitude}&longitude=${longitude}&radius=${radius}`;
    if (date) url += `&date=${date}`;

    try {
        const headers = getAuthHeaders();
        const crops = await makeRequest(url, "GET", null, headers);
        const container = document.getElementById("nearbyCropsContainer");
        container.innerHTML = "<h3>Nearby Crop Opportunities:</h3>";
        if (crops.length > 0) {
            crops.forEach(crop => {
                const cropItem = document.createElement("div");
                cropItem.classList.add("crop-item");
                cropItem.innerHTML = `<strong>Crop:</strong> ${crop.name}, <strong>Flowering:</strong> ${crop.floweringStart} - ${crop.floweringEnd}, <strong>Lat:</strong> ${crop.latitude}, <strong>Lng:</strong> ${crop.longitude}, <strong>Density:</strong> ${crop.recommendedHiveDensity}`;
                container.appendChild(cropItem);
            });
        } else {
            container.innerHTML += "<p>No nearby crop opportunities found.</p>";
        }
    } catch (error) {
        // Error already handled
    }
}
