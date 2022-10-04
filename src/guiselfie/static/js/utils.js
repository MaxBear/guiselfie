var Utils = (function() {
    var MonthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"];

    //private
    function publicGetCsvFileName() {
        var today = new Date();        
        var dd = today.getDate();
        var mm = today.getMonth() + 1; //January is 0!
        var yyyy = today.getFullYear();

        if(dd<10) {
            dd='0'+dd
        } 

        if(mm<10) {
            mm='0'+mm
        } 
        
        var options = {
            timeZone: 'Europe/London',
            year: 'numeric', month: 'numeric', day: 'numeric',
            hour: 'numeric', minute: 'numeric', second: 'numeric',
        },
        formatter = new Intl.DateTimeFormat([], options)        
        var dt = formatter.format(new Date());
        
        var csv = "es_routes_check_videxio_" + yyyy + "-" + mm + "-" + dd + ".csv";
        return csv;
    }
    
    function publicDisplayTitle(fname) {
        var tokens = fname.split("_");
        var subscriber = tokens[3].toUpperCase();
        var ts = tokens[4].split(".")[0];
        return [subscriber, ts];
    }
    
    function publicDisplayDate(dt) {
        var dd = dt.getDate();
        var mm = dt.getMonth() + 1;
        var yyyy = dt.getFullYear();
        var h = dt.getHours();
        var m = dt.getMinutes();
        var s = dt.getSeconds();
        
        if (h<10) { h = '0' + h }
        if (m<10) { m = '0' + m }
        if (s<10) { s = '0' + s }
        
        return yyyy + "-" + mm + "-" + dd + " " + h + ":" + m + ":" + s;        
    }
    
    function publicTruncateDatetime(dt, unit) {
        var dd = dt.getDate();
        var mm = dt.getMonth() + 1;
        var yyyy = dt.getFullYear();
        var h = dt.getHours();
        var m = dt.getMinutes();
        var s = dt.getSeconds();        
        if (unit=="day") {
            return yyyy + "-" + mm + "-" + dd;        
        } else if (unit=="month") {
            return yyyy + "-" + mm;
        } else if (unit=="year") {
            return yyyy;
        } else if (unit=="hour") {
            return yyyy + "-" + mm + "-" + dd + " " + h;        
        } else if (unit=="minute") {
            return yyyy + "-" + mm + "-" + dd + " " + h + ":" + m;        
        }
    }

    var formatUtcDate;
    $.getScript("/static/js/d3.v3.min.js", function(){
        formatUtcDate = d3.time.format.utc("%Y-%m-%dT%H:%M:%S");
    });
    
    function publicCsvType(d) {
        d.start_utc = formatUtcDate.parse(d.start_utc);
        d.rtt_avg = +d.rtt_avg;
        d.loss = +d.loss;
        return d;
    }
    
    function publicCurrentYear() {        
        var d = new Date();        
        return d.getFullYear();
    }

    function publicCurrentMonth() {        
        var d = new Date();            
        return d.getMonth() + 1;
    }
    
    function publicEnglishMonth(m) {
        var mBase0  = m - 1;
        return MonthNames[mBase0];
    }

    function gen_modal(id, title, body_id, button_id, show_button, button_label) {
       var html = '<div class="modal fade" id="' + id + '" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">'
       html += '<div class="modal-dialog" role="document">'
       html += '<div class="modal-content">'
       html += '<div class="modal-header">'
       html += '<button type="button" class="close" data-dismiss="modal" aria-label="Close">'
       html += '<span aria-hidden="true">&times;</span>'
       html += '</button>'
       html += '<h5 class="modal-title" id="' + title + '">' + title + '</h5>'
       html += '</div>'
       html += '<div class="modal-body" id="' + body_id + '">'
       html += '</div>'
       html += '<div class="modal-footer">'
       if (show_button===true) {
          html += '<button type="button" class="btn btn-primary" id="' + button_id + '">' + button_label + '</button>'
       }   
       html += '<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>'
       html += '</div>'
       html += '</div>'
       html += '</div>'
       html += '</div>'
       return html
    }   

    //public
    return {
        getCsvFileName: publicGetCsvFileName,
        csvType: publicCsvType,
        displayDate: publicDisplayDate, 
        displayTitle: publicDisplayTitle, 
        truncateDatetime: publicTruncateDatetime, 
        currentMonth: publicCurrentMonth,
        currentYear: publicCurrentYear, 
        englishMonth: publicEnglishMonth,
        gen_modal: gen_modal,
    };
})();
