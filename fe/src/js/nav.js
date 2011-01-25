window.addEvent('domready', function() {
	
	//create our Accordion instance
	var myAccordion = new Accordion($('accordion'), 'h3.toggler', 'div.element', {
		opacity: false,
		onActive: function(toggler, element){
			toggler.setStyle('color', '#41464D');
		},
		onBackground: function(toggler, element){
			toggler.setStyle('color', '#528CE0');
		}
	});
        
        // hover
        $$('.toggler').addEvent('mouseenter', function() { this.fireEvent('click'); });

        var navbar = new Fx.Reveal($('navbar'), {duration: 500, mode: 'horizontal'});
        $('shownav').addEvent('click', function() {navbar.toggle()});

});
