function getAuthHeaders() {
    const token = localStorage.getItem("access_token");
    const tokenType = localStorage.getItem("token_type");
    
    if (token && tokenType) {
        return {
            "Authorization": `${tokenType} ${token}`,
            "Content-Type": "application/json"
        };
    } else {
        alert("You are not authenticated. Please log in.");
        window.location.href = "/login"; 
        return null;
    }
}

function handleUnauthenticated(response) {
    if (response.status === 401) {
        alert("You are not authenticated. Please log in.");
        window.location.href = "/login"; 
        return true;
    }
    return false;
}

document.addEventListener('DOMContentLoaded', () => {
    const addCropForm = document.getElementById('addCropForm');
    const addHiveForm = document.getElementById('addHiveForm');

    addCropForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            name: document.getElementById('cropName').value,
            floweringStart: document.getElementById('floweringStart').value,
            floweringEnd: document.getElementById('floweringEnd').value,
            latitude: parseFloat(document.getElementById('cropLatitude').value),
            longitude: parseFloat(document.getElementById('cropLongitude').value),
            recommendedHiveDensity: parseInt(document.getElementById('recommendedHiveDensity').value),
        };

        try {
            const response = await fetch('/api/crops', {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(data),
            });

            if (handleUnauthenticated(response)) return;
            
            const result = await response.json();

            if (response.ok) {
                alert('Crop added successfully!');
            } else {
                let errorMsg = 'Failed to add Crop.';
                if (Array.isArray(result.detail)) {
                    errorMsg = result.detail.map(err => {
                        const field = err.loc ? err.loc.join('.') : 'field';
                        return `${field}: ${err.msg}`;
                    }).join('\n');
                } else if (typeof result.detail === 'string') {
                    errorMsg = result.detail;
                }
                alert(errorMsg);
            }  
        } catch (error) {
            console.error('Error adding crop:', error);
            alert('Network or server error while adding crop.');
        }
    });

    addHiveForm.addEventListener('submit', async (e) => {
        e.preventDefault();
    
        const data = {
            hiveId: document.getElementById('hiveId').value,
            datePlaced: document.getElementById('datePlaced').value,
            latitude: parseFloat(document.getElementById('latitude').value),
            longitude: parseFloat(document.getElementById('longitude').value),
            numColonies: parseInt(document.getElementById('numColonies').value),
        };
    
        try {
            const response = await fetch('/api/hives', {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(data),
            });

            if (handleUnauthenticated(response)) return;

            const result = await response.json();

            if (response.ok) {
                alert('Hive log added successfully!');
            } else {
                let errorMsg = 'Failed to add hive.';
                
                if (Array.isArray(result.detail)) {
                    errorMsg = result.detail.map(err => {
                        const field = err.loc ? err.loc.join('.') : 'field';
                        return `${field}: ${err.msg}`;
                    }).join('\n');
                } else if (typeof result.detail === 'string') {
                    errorMsg = result.detail;
                }
            
                alert(errorMsg);
            }            
        } catch (error) {
            console.error('Error adding hive:', error);
            alert('Network or server error while adding hive.');
        }
    });    
});

async function fetchHiveLogs() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    let url = '/api/hives';

    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (params.toString()) url += `?${params.toString()}`;

    try {
        const response = await fetch(url, { headers: getAuthHeaders() });

        if (handleUnauthenticated(response)) return;

        const data = await response.json();
        document.getElementById('hiveLogsContainer').innerText = JSON.stringify(data, null, 2);
    } catch (error) {
        console.error('Error fetching hive logs:', error);
    }
}

async function exportHivesCSV() {
    const start = document.getElementById('exportStartDate').value;
    const end = document.getElementById('exportEndDate').value;

    let url = '/api/hives/export';
    const params = new URLSearchParams();
    if (start) params.append('start_date', start);
    if (end) params.append('end_date', end);
    if (params.toString()) url += `?${params.toString()}`;

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: getAuthHeaders()
        });

        if (handleUnauthenticated(response)) return;

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = 'hives_export.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
        alert('Error exporting CSV: ' + error.message);
    }
}

async function fetchNearbyCrops() {
    const latitude = parseFloat(document.getElementById('currentLatitude').value);
    const longitude = parseFloat(document.getElementById('currentLongitude').value);
    const radius = parseFloat(document.getElementById('radius').value) || 100;
    const date = document.getElementById('searchDate').value;

    let url = `/api/crops/nearby/?latitude=${latitude}&longitude=${longitude}&radius=${radius}`;
    if (date) url += `&date=${date}`;

    try {
        const response = await fetch(url, { headers: getAuthHeaders() });

        if (handleUnauthenticated(response)) return;

        const data = await response.json();
        document.getElementById('nearbyCropsContainer').innerText = JSON.stringify(data, null, 2);
    } catch (error) {
        console.error('Error fetching nearby crops:', error);
    }
}
