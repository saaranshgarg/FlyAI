// address_dropdown.js
// This JS expects a global variable VILLAGE_DATA to be defined as the state-district-village mapping.
document.addEventListener('DOMContentLoaded', function() {
    const stateSel = document.getElementById('state');
    const districtSel = document.getElementById('district');
    const villageSel = document.getElementById('village');

    function updateDistricts() {
        const state = stateSel.value;
        districtSel.innerHTML = '';
        villageSel.innerHTML = '';
        if (!VILLAGE_DATA[state]) return;
        Object.keys(VILLAGE_DATA[state]).forEach(function(d) {
            districtSel.innerHTML += `<option value="${d}">${d}</option>`;
        });
        updateVillages();
    }

    function updateVillages() {
        const state = stateSel.value;
        const district = districtSel.value;
        villageSel.innerHTML = '';
        if (!VILLAGE_DATA[state] || !VILLAGE_DATA[state][district]) return;
        VILLAGE_DATA[state][district].forEach(function(v) {
            villageSel.innerHTML += `<option value="${v}">${v}</option>`;
        });
    }

    stateSel.addEventListener('change', updateDistricts);
    districtSel.addEventListener('change', updateVillages);
    updateDistricts(); // initialize on load
});
