show_memberships = function(opt_data, opt_sb, opt_caller) {
    var output = '';
    output += '\n';
    var oList = opt_data.memberships;
    var oListLen = oList.length;
    for (var oIndex = 0; oIndex < oListLen; oIndex++) {
        var oData = oList[oIndex];
        output += '\n<div class="p1">\n    <div class="dp30 leftcol">' + oData.name + '</div>\n    <div class="dp30 leftcol">' + oData.roles + '</div>\n    <div class="dp30 leftcol">' + oData.plans + '</div>\n</div>\n';
    }
    output += '\n';
    return output;
}