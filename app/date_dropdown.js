// date_dropdown.js
// Dynamically update days based on selected year and month, only allow future dates

document.addEventListener('DOMContentLoaded', function() {
    const yearSel = document.getElementById('year');
    const monthSel = document.getElementById('month');
    const daySel = document.getElementById('day');

    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1; // JS months are 0-based
    const currentDay = now.getDate();

    // Remove past years
    for (let i = 0; i < yearSel.options.length; i++) {
        if (parseInt(yearSel.options[i].value, 10) < currentYear) {
            yearSel.options[i].disabled = true;
        }
    }

    function daysInMonth(year, month) {
        return new Date(year, month, 0).getDate(); // month is 1-based
    }

    function updateMonths() {
        // Remove past months for current year
        for (let i = 0; i < monthSel.options.length; i++) {
            let m = parseInt(monthSel.options[i].value, 10);
            if (parseInt(yearSel.value, 10) === currentYear && m < currentMonth) {
                monthSel.options[i].disabled = true;
            } else {
                monthSel.options[i].disabled = false;
            }
        }
        if (monthSel.options[monthSel.selectedIndex].disabled) {
            // Select first enabled month
            for (let i = 0; i < monthSel.options.length; i++) {
                if (!monthSel.options[i].disabled) {
                    monthSel.selectedIndex = i;
                    break;
                }
            }
        }
    }

    function updateDays() {
        const year = parseInt(yearSel.value, 10);
        const month = parseInt(monthSel.value, 10);
        const numDays = daysInMonth(year, month);
        let options = '';
        let minDay = 1;
        if (year === currentYear && month === currentMonth) {
            minDay = currentDay;
        }
        for (let d = minDay; d <= numDays; d++) {
            const dd = d.toString().padStart(2, '0');
            options += `<option value="${dd}">${dd}</option>`;
        }
        daySel.innerHTML = options;
    }

    yearSel.addEventListener('change', function() {
        updateMonths();
        updateDays();
    });
    monthSel.addEventListener('change', updateDays);
    updateMonths();
    updateDays(); // initialize on load
});
