frappe.pages['stock-level'].on_page_load = function(wrapper) {

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Stock Level',
		single_column: true
	});

	frappe.require([
		'/assets/optilens_app/js/stock_level_app.js',
		'/assets/optilens_app/css/stock_level_page.css'
	], async () => {

		try {

			// LOAD RAW HTML FILE
			const response = await fetch(
				'/assets/optilens_app/html/stock_level_page.html'
			);

			const html = await response.text();

			$(page.body).html(html);

			console.log('Assets loaded');

			if (window.start_stock_level_app) {
				window.start_stock_level_app();
			}

		} catch (e) {

			console.error('Failed to load page:', e);

		}

	});

};