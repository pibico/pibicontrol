// Copyright (c) 2020, PibiCo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sensor Log', {
	refresh: function(frm) {
    var label, data1, data2, data3 = []
    var var1, uom1, var2, uom2, var3, uom3 = ''
    
    frappe.call({
      method: "pibicontrol.pibicontrol.api.get_chart_dataset",
      args: {
        'doc': frm.doc.name
      },
      async: false,
    	callback: function(r) {
        label = r.message.label;
        data1 = r.message.main_read;
        var1 = r.message.variable; 
        uom1 = r.message.uom;
        data2 = r.message.second_read;
        var2 = r.message.second_var;
        uom2 = r.message.second_uom;
        data3 = r.message.third_read;
        var3 = r.message.third_var;
        uom3 = r.message.third_uom;
        //console.log(r.message)
    	}
    });
    
    // Main Data
    const main_data = {
      labels: label,
      datasets: [
        {
          name: var1,
          type: "line",
          values: data1
        }
      ],
      yMarkers: [
        {
          label: "maximum: " + frm.doc.max + ' ' + uom1,
          value: frm.doc.max,
          options: { labelPos: 'right' } // default: 'right'
        }
      ],
      tooltipOptions: {
        formatTooltipX: d => (d + '').toUpperCase(),
        formatTooltipY: d => d + ' pts',
      }
    };
    const main_chart = new frappe.Chart(
      "#main_chart", {
      title: var1 + ' (' + uom1 + ')',
      data: main_data,
      type: 'bar', // or 'bar', 'line', 'scatter', 'pie', 'percentage'
      height: 300,
      colors: ['#4682b4'],
      axisOptions: {
        xAxisMode: 'tick', // default: 'span'
        xIsSeries: true // default: false
      },
      lineOptions: {
        hideDots: 1, // default: 0
      }
    });
    // Secondary Data
    const second_data = {
      labels: label,
      datasets: [
        {
          name: var2,
          type: "line",
          values: data2
        },
        {
          name: var3,
          type: "line",
          values: data3
        }
      ]
    };
    const second_chart = new frappe.Chart(
      "#second_chart", {
      // or a DOM element,
      // new Chart() in case of ES6 module with above usage
      title: var2 + " (" + uom2 + ") | " + var3 + " (" + uom3 + ")",
      data: second_data,
      type: 'axis-mixed', // or 'bar', 'line', 'scatter', 'pie', 'percentage'
      height: 300,
      colors: ['#ff2233', '#224433'],
      axisOptions: {
        xAxisMode: 'tick', // default: 'span'
        xIsSeries: true // default: false
      },
      lineOptions: {
        spline: 0,
        hideDots: 1
      }
    });
	}
});