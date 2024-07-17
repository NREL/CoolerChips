// static/js/custom_cost.js
let currentFileInput;

function saveState() {
    const formData = new FormData(document.getElementById('fileForm'));
    const table1Data = document.getElementById('file1-details').innerHTML;
    const table2Data = document.getElementById('file2-details').innerHTML;
    const totalCost1 = document.getElementById('file1-totalCost').textContent;
    const totalCost2 = document.getElementById('file2-totalCost').textContent;

    sessionStorage.setItem('formData', JSON.stringify(Object.fromEntries(formData.entries())));
    sessionStorage.setItem('table1Data', table1Data);
    sessionStorage.setItem('table2Data', table2Data);
    sessionStorage.setItem('totalCost1', totalCost1);
    sessionStorage.setItem('totalCost2', totalCost2);
}

function restoreState() {
    const formData = JSON.parse(sessionStorage.getItem('formData'));
    const table1Data = sessionStorage.getItem('table1Data');
    const table2Data = sessionStorage.getItem('table2Data');
    const totalCost1 = sessionStorage.getItem('totalCost1');
    const totalCost2 = sessionStorage.getItem('totalCost2');

    if (formData) {
        for (const [key, value] of Object.entries(formData)) {
            document.querySelector(`[name="${key}"]`).value = value;
        }
    }
    if (table1Data) {
        document.getElementById('file1-details').innerHTML = table1Data;
    }
    if (table2Data) {
        document.getElementById('file2-details').innerHTML = table2Data;
    }
    if (totalCost1) {
        document.getElementById('file1-totalCost').textContent = totalCost1;
    }
    if (totalCost2) {
        document.getElementById('file2-totalCost').textContent = totalCost2;
    }
}

document.addEventListener('DOMContentLoaded', restoreState);

function showModal(input, fileId) {
    currentFileInput = input;
    currentFileInput.fileId = fileId;
    $('#inputModal').modal('show');
}

function submitModalForm() {
    const mtbf = document.getElementById('modalMTBF').value;
    const gamma = document.getElementById('modalGamma').value;
    const beta = document.getElementById('modalBeta').value;
    const eta = document.getElementById('modalEta').value;
    const costPerMaintenanceEvent = document.getElementById('modalCostPerMaintenanceEvent').value;

    if (mtbf && gamma && beta && eta && costPerMaintenanceEvent) {
        const reader = new FileReader();
        reader.onload = function() {
            const content = reader.result;

            // Remove existing hidden inputs if they exist
            removeHiddenInputs(currentFileInput.fileId);

            // Add new hidden inputs
            addHiddenInput(currentFileInput.fileId, 'mtbf', mtbf.trim());
            addHiddenInput(currentFileInput.fileId, 'gamma', gamma.trim());
            addHiddenInput(currentFileInput.fileId, 'beta', beta.trim());
            addHiddenInput(currentFileInput.fileId, 'eta', eta.trim());
            addHiddenInput(currentFileInput.fileId, 'costPerMaintenanceEvent', costPerMaintenanceEvent.trim());

            const formData = new FormData();
            formData.append('fileContent', content);
            formData.append('mtbf', mtbf.trim());
            formData.append('gamma', gamma.trim());
            formData.append('beta', beta.trim());
            formData.append('eta', eta.trim());
            formData.append('costPerMaintenanceEvent', costPerMaintenanceEvent.trim());

            fetch('/results/cost/process_file', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log("Server response received", data);
                displayCoolingSystemDetails(data.cooling_system_details, currentFileInput.fileId);
                calculateTotalCost(data.total_cooling_cost);
                updateGraphs(data.roi_image, data.irr_image, data.npv_image);
            })
            .catch(error => {
                console.error("Error occurred:", error);
            });

            $('#inputModal').modal('hide');
        };
        reader.onerror = function() {
            console.error("Could not read file");
        };
        reader.readAsText(currentFileInput.files[0]);
    } else {
        alert("All values are required.");
    }
}

function removeHiddenInputs(fileId) {
    const hiddenInputs = document.querySelectorAll(`#${fileId}-group input[type='hidden']`);
    hiddenInputs.forEach(input => input.remove());
}

function addHiddenInput(fileId, name, value) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.id = `${fileId}-${name}`;
    input.name = name;
    input.value = value;
    document.getElementById(fileId + '-group').appendChild(input);
}

function handleFormSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    fetch('/results/cost/process_file', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("Form submitted successfully", data);
        updateGraphs(data.roi_image, data.irr_image, data.npv_image);
    })
    .catch(error => {
        console.error("Error occurred:", error);
    });
}

function updateGraphs(roi_image, irr_image, npv_image) {
    document.getElementById('roi-graph').src = "data:image/png;base64," + roi_image;
    document.getElementById('irr-graph').src = "data:image/png;base64," + irr_image;
    document.getElementById('npv-graph').src = "data:image/png;base64," + npv_image;
}

function displayCoolingSystemDetails(details, fileId) {
    let tbody = "";
    details.forEach((row, index) => {
        if (index === 0) return; // Skip the header row
        tbody += "<tr>";
        row.forEach((cell, cellIndex) => {
            if (cellIndex === 2) { // Redundancy column
                tbody += `<td>
                            <select class="form-control" onchange="updateRedundancy(${index - 1}, this.value, '${fileId}')">
                                <option value="N" ${cell === 'N' ? 'selected' : ''}>N</option>
                                <option value="N+1" ${cell === 'N+1' ? 'selected' : ''}>N+1</option>
                                <option value="N+2" ${cell === 'N+2' ? 'selected' : ''}>N+2</option>
                                <option value="2N" ${cell === '2N' ? 'selected' : ''}>2N</option>
                                <option value="2N+1" ${cell === '2N+1' ? 'selected' : ''}>2N+1</option>
                            </select>
                          </td>`;
            } else {
                tbody += `<td ondblclick="makeEditable(this)">${cell}</td>`;
            }
        });
        tbody += "</tr>";
    });

    document.getElementById(`${fileId}-details`).innerHTML = tbody;
}

function calculateTotalCost(totalCost) {
    document.getElementById('file1-totalCost').textContent = totalCost;
    document.getElementById('file2-totalCost').textContent = totalCost;
}

function clearTable(fileId) {
    document.getElementById(`${fileId}-details`).innerHTML = "";
    document.getElementById(`${fileId}-totalCost`).textContent = "";
}

function makeEditable(cell) {
    const originalContent = cell.textContent;
    const input = document.createElement('input');
    input.type = 'text';
    input.value = originalContent;
    input.className = 'form-control editable';
    input.addEventListener('blur', function() {
        cell.textContent = input.value;
        updateCell(cell, input.value);
    });
    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            cell.textContent = input.value;
            updateCell(cell, input.value);
        } else if (event.key === 'Escape') {
            cell.textContent = originalContent;
        }
    });
    cell.textContent = '';
    cell.appendChild(input);
    input.focus();
}

function updateCell(cell, newValue) {
    const row = cell.parentNode;
    const table = row.parentNode;
    const rowIndex = Array.prototype.indexOf.call(table.children, row);
    const cellIndex = Array.prototype.indexOf.call(row.children, cell);

    // Send an AJAX request to update the cell data on the server
    fetch('/results/cost/update_cell', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            rowIndex: rowIndex,
            cellIndex: cellIndex,
            newValue: newValue
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Cell updated successfully", data);
    })
    .catch(error => {
        console.error("Error occurred while updating cell", error);
    });
}
