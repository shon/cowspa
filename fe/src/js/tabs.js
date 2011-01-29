var cur_uri = new URI();
function open_current_tab(tab) {
    var href = tab.get('href');
    var pat = new RegExp('.*' + href + '$');
    if (cur_uri.toString().match(pat)) {
        tab.set('class', 'tab-open');
    };
};
var tabs = $$('.tab-closed');
tabs.each(open_current_tab);
