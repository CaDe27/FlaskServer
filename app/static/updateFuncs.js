function endDateAfterStartDate() {
    // Set the minimum value (min attribute) of the endDate to the selected start date
    startDateValue = document.getElementById('startDate').value;
    endDateElem = document.getElementById('endDate');
    if(endDateElem.value < startDateValue){
        endDateElem.value = startDateValue;
    }
}

function startDateBeforeEndDate() {
    // Set the minimum value (min attribute) of the endDate to the selected start date
    startDateElem = document.getElementById('startDate');
    endDateValue= document.getElementById('endDate').value;
    if(startDateElem.value > endDateValue){
        startDateElem.value = endDateValue;
    }
}

function startHourBeforeEndHour() {
    startDateValue = document.getElementById('startDate').value;
    endDateValue= document.getElementById('endDate').value;
    if(startDateValue != endDateValue)
        return;

    startHourElem = document.getElementById('startHourSelect');
    endHourValue= document.getElementById('endHourSelect').value;
    if(startHourElem.value > endHourValue){
         startHourElem.value = endHourValue;
    }
}

function endHourAfterStartHour() {
    startDateValue = document.getElementById('startDate').value;
    endDateValue= document.getElementById('endDate').value;
    if(startDateValue != endDateValue)
        return;

    endHourElem = document.getElementById('endHourSelect');
    startHourValue= document.getElementById('startHourSelect').value;
    if(endHourElem.value < startHourValue){
         endHourElem.value = startHourValue;
    }
}

function startMinuteBeforeEndMinute() {
    startDateValue = document.getElementById('startDate').value;
    endDateValue= document.getElementById('endDate').value;
    if(startDateValue != endDateValue)
        return;

    startMinuteElem = document.getElementById('startMinuteSelect');
    endMinuteValue= document.getElementById('endMinuteSelect').value;
    if(startMinuteElem.value > endMinuteValue){
         startMinuteElem.value = endMinuteValue;
    }
}

function endMinuteAfterStartMinute() {
    startDateValue = document.getElementById('startDate').value;
    endDateValue= document.getElementById('endDate').value;
    if(startDateValue != endDateValue)
        return;

    endMinuteElem = document.getElementById('endMinuteSelect');
    startMinuteValue= document.getElementById('startMinuteSelect').value;
    if(endMinuteElem.value < startMinuteValue){
         endMinuteElem.value = startMinuteValue;
    }
}

async function changeTimeEventListener(){
    const padWithZero = (value) => String(value).padStart(2, '0');
    var startDate = document.getElementById('startDate').value;
    var startHour = padWithZero(document.getElementById('startHourSelect').value);
    var startMinute = padWithZero(document.getElementById('startMinuteSelect').value);

    var endDate = document.getElementById('endDate').value;
    var endHour = padWithZero(document.getElementById('endHourSelect').value);
    var endMinute = padWithZero(document.getElementById('endMinuteSelect').value);

    var startTime = startDate + 'T' + startHour + ':' + startMinute + ':00';
    var endTime = endDate + 'T' + endHour + ':' + endMinute + ':59';

    return fetch('/get_graph_new_datetime', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({startTime, endTime}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update cytoscape with new elements
        runBreadthFirstLayout();
    });
}

async function changeInDepthEventListener(){
    new_depth_limit = document.getElementById('inDepthLimit').value;
    return fetch('/get_graph_new_in_depth_limit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({new_depth_limit}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update cytoscape with new elements
        runBreadthFirstLayout();
    });
}

async function changeOutDepthEventListener(){
    new_depth_limit = document.getElementById('outDepthLimit').value;
    return fetch('/get_graph_new_out_depth_limit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({new_depth_limit}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update cytoscape with new elements
        runBreadthFirstLayout();
    });
}

async function changeServiceSelectorEventListener(){
    newService = document.getElementById('serviceSelector').value;
    return fetch('/get_graph_new_selected_service', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({newService}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update cytoscape with new elements
        runBreadthFirstLayout();
    });
}

function getCheckboxLabelValue(checkboxId) {
    var checkbox = document.getElementById(checkboxId);
    labelValue = null;
    if (checkbox) {
        // Get the next sibling element, which is the label in this case
        var label = checkbox.nextElementSibling;
        if (label) {
            labelValue= label.innerText || label.textContent;
        } else {
            console.error("Label not found for checkbox with ID: " + checkboxId);
        }
    } else {
        console.error("Checkbox not found with ID: " + checkboxId);
    }
    return labelValue;
}

function onStatusCodeCheckboxChange(checkboxId) {
    var checkbox = document.getElementById(checkboxId);
    isChecked = checkbox.checked;
    statusCode =  getCheckboxLabelValue(checkboxId);
    console.log('statusCode', statusCode)
    return fetch('/get_graph_update_status_code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // send data as JSON
        body: JSON.stringify({statusCode, isChecked}) 
    })
    .then(response => response.json())
    .then(data => {
        cy.elements().remove();
        cy.add(data.elements);  // update cytoscape with new elements
        runBreadthFirstLayout();
    });
    
}
