function lineChart(d, id) {
    "use strict";

    var chart;
    nv.addGraph(function() {
        chart = nv.models.lineChart();
        chart
            .margin({right:40, top:40, left:40, bottom:40})
            .useInteractiveGuideline(true)
            .duration(250)
            ;

        chart.xAxis
            .tickFormat(function(d) {
            return d3.time.format('%Y-%m-%d')(new Date(d))
        });

//         chart.showXAxis(true);

        d3.select(id)
            .datum(d)
            .transition()
            .call(chart);

        nv.utils.windowResize(chart.update);
        chart.dispatch.on('stateChange', function(e) { nv.log('New State:', JSON.stringify(e)); });
        d['nvd3chart'] = chart;
        return chart;
    });
}

function historicalBarChart(d, id) {
    "use strict";
    
    var chart;
    nv.addGraph(function() {
        chart = nv.models.historicalBarChart();
        chart
            .margin({right:40, top:40, left:40, bottom:40})
            .useInteractiveGuideline(true)
            .duration(250)
            ;

        chart.xAxis
            .tickFormat(function(d) {
            return d3.time.format('%Y-%m-%d')(new Date(d))
        });

        chart.showXAxis(true);

        d3.select(id)
            .datum(d)
            .transition()
            .call(chart);

        nv.utils.windowResize(chart.update);
        chart.dispatch.on('stateChange', function(e) { nv.log('New State:', JSON.stringify(e)); });
        d['nvd3chart'] = chart;
        return chart;
    });
}

function multiBarChart(d, id) {
    "use strict";
        
    var chart;
    nv.addGraph(function() {
        chart = nv.models.multiBarChart();
        chart
            .margin({right:40, top:40, left:40, bottom:40})
            .duration(250)
            .stacked(true)
            ;

        // chart sub-models (ie. xAxis, yAxis, etc) when accessed directly, return themselves, not the parent chart, so need to chain separately

        chart.xAxis
            .tickFormat(function(d) {
            return d3.time.format('%Y-%m-%d')(new Date(d))
        });
        ;

        chart.yAxis
            .tickFormat(d3.format('d'));

        chart.showXAxis(true);
        
        d3.select(id)
            .datum(d)
            .transition()
            .call(chart)

        nv.utils.windowResize(chart.update);
        chart.dispatch.on('stateChange', function(e) { nv.log('New State:', JSON.stringify(e)); });

        d['nvd3chart'] = chart;
        return chart;
    });
}

function setupFilters(chartsDataBlocks, ids) {
//     ids = Object.keys(filters)
    for (i=0 ; i < ids.length ; ++i)
    {
        setupFilter(chartsDataBlocks, ids[i]);
    }
}

function setupFilter(chartsDataBlocks, id) {
    document
        .getElementById(id)
        .addEventListener('change', function(e) {
            charts = [];
            v = e.target.value;
            debugger;
            for (i=0 ; i < chartsDataBlocks.length ; ++i)
            {
                chartsData = chartsDataBlocks[i];
                for (j=0 ; j < chartsData.length ; ++j)
                {
                    datum = chartsData[j].datum;
                    for (d=0 ; d < datum.length ; ++d)
                    {
                        data = datum[d];
                        disabled = data.key !== v;
                        if (v === 'all') {
                            disabled = false;
                        }
                        data.disabled = disabled;
                    }
                    datum.nvd3chart.update();
                }
            }
        },
        false);
}

function populateCharts(chartsDataBlocks) {
    for (i=0 ; i < chartsDataBlocks.length ; ++i)
    {
        chartsData = chartsDataBlocks[i];
        for (j=0 ; j < chartsData.length ; ++j)
        {
            d = chartsData[j];
            window[d.drawFunction](d.datum, '#' + d.id, d.domain);
        }
    }
}

function createRequest() {
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState != 4) return;
        if (req.status != 200) {
            return;
        }
        processData(JSON.parse(req.responseText));
    }
    return req;
}

function goToFromTextFields() {
    date_from = document.getElementById("date_from").value;
    date_to = document.getElementById("date_to").value;
    goToDates(date_from, date_to);
}

function goToDates(date_from_str, date_to_str) {
    page = window.location.pathname.split("/")[1]
    url = window.location.protocol + "//" + window.location.host + "/" + page + "/" + date_from + "/" + date_to;
    if (url != location) {
        location = url;
    }
}

/*
function pad(num, size) {
    var s = num + "";
    while (s.length < size) s = "0" + s;
    return s;
}

function date2string(date) {
    console.log(date)
    y = pad(date.getFullYear(), 4);
    m = pad(date.getMonth(), 2);
    d = pad(date.getDate());
    return y + '-' + m + '-' + d;
}
*/

/*
function goToCurrentWeek() {
    goToWeek(new Date());
}

function goToLastWeek() {
    date = new Date();
    date.setDate(date.getDate() - 7);
    goToWeek(date);
}

function goToWeek(date) {
    delta_start = date.getDay() - 1;
    delta_end = 7 - date.getDay();
    date_from = new Date(date.getFullYear(),
                         date.getMonth(),
                         date.getDate() - delta_start);
    date_to = new Date(date.getFullYear(),
                       date.getMonth(),
                       date.getDate() + delta_end);
    goToDates(date_from, date_to);
}

function goToMonth(date) {
    
}

function initDateFilters() {
    split = window.location.pathname.split("/")
    document.getElementById("date_to").value = split[split.length - 1];
    document.getElementById("date_from").value = split[split.length - 2];
}*/
