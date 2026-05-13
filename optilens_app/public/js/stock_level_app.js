console.log('Loading stock level app...');

window.start_stock_level_app = function() {

	console.log('Stock level app started');

	function mount_vue() {

		Vue.createApp({

			delimiters: ['[[', ']]'],

			data() {

				return {

					options: {
						companies: [],
						warehouses: []
					},

					filters: {
						companies: [],
						warehouses: [],
						item_groups: [],
						search: ''
					},

					stockData: [],

					searchTerms: {
						company: '',
						warehouse: '',
						item_group: ''
					},

					collapsedSections: {
						company: false,
						warehouse: false,
						item_group: false
					},

					activeSearchRow: null,
					searchResults: [],

					loading: false

				}

			},

			async mounted() {

				console.log('Vue mounted');
				await this.fetchInitialData();

			},

			computed: {

				filteredCompanies() {
					if (!this.searchTerms.company) return this.options.companies;
					const search = this.searchTerms.company.toLowerCase();
					return this.options.companies.filter(c => c.toLowerCase().includes(search));
				},

				filteredWarehouses() {
					if (!this.searchTerms.warehouse) return this.options.warehouses;
					const search = this.searchTerms.warehouse.toLowerCase();
					return this.options.warehouses.filter(w => w.toLowerCase().includes(search));
				},

				filteredItemGroups() {
					if (!this.searchTerms.item_group) return this.options.item_groups;
					const search = this.searchTerms.item_group.toLowerCase();
					return this.options.item_groups.filter(g => g.toLowerCase().includes(search));
				}

			},

			methods: {

				async fetchInitialData() {
					try {
						const response = await frappe.call({
							method: 'optilens_app.api.dashboard.get_stock_filter_options'
						});
						if (response.message) {
							this.options.companies = response.message.companies || [];
							this.options.item_groups = response.message.groups || [];
							
							if (this.options.companies.length > 0) {
								this.filters.companies = [this.options.companies[0]];
								await this.onCompanyChange();
							}
						}
					} catch (e) {
						console.error('Error fetching initial data:', e);
					}
				},

				async onCompanyChange() {
					if (!this.filters.companies || this.filters.companies.length === 0) {
						this.options.warehouses = [];
						this.filters.warehouses = [];
						this.stockData = [];
						return;
					}
					try {
						const response = await frappe.call({
							method: 'frappe.client.get_list',
							args: {
								doctype: 'Warehouse',
								filters: { company: ['in', this.filters.companies], is_group: 0 },
								fields: ['name']
							}
						});
						this.options.warehouses = (response.message || []).map(w => w.name);
						// Remove any warehouses that no longer belong to selected companies
						this.filters.warehouses = this.filters.warehouses.filter(w => this.options.warehouses.includes(w));
						await this.fetchStock();
					} catch (e) {
						console.error('Error fetching warehouses:', e);
					}
				},

				async fetchStock() {
					if (!this.filters.companies || this.filters.companies.length === 0 || this.filters.warehouses.length === 0) {
						this.stockData = [];
						return;
					}

					this.loading = true;
					try {
						const response = await frappe.call({
							method: 'optilens_app.api.stock_level_page.get_warehouse_stock_levels',
							args: {
								company: this.filters.companies[0],
								warehouses: this.filters.warehouses,
								item_groups: this.filters.item_groups,
								search: this.filters.search
							}
						});
						this.stockData = response.message || [];
					} catch (e) {
						console.error('Error fetching stock levels:', e);
						frappe.show_alert({ message: 'Error fetching stock levels', indicator: 'red' });
					} finally {
						this.loading = false;
					}
				},

				selectAllCompanies() {
					this.filters.companies = [...this.options.companies];
					this.onCompanyChange();
				},

				deselectAllCompanies() {
					this.filters.companies = [];
					this.onCompanyChange();
				},

				selectAllWarehouses() {
					this.filters.warehouses = [...this.options.warehouses];
				},

				deselectAllWarehouses() {
					this.filters.warehouses = [];
				},

				selectAllItemGroups() {
					this.filters.item_groups = [...this.options.item_groups];
					this.fetchStock();
				},

				deselectAllItemGroups() {
					this.filters.item_groups = [];
					this.fetchStock();
				},

				toggleSection(section) {
					this.collapsedSections[section] = !this.collapsedSections[section];
				},

				getBalanceClass(value) {
					if (value === undefined || value === null) return '';
					return value <= 0 ? 'text-danger' : 'text-success';
				},

				addNewItem() {
					const newItem = {
						item_code: "",
						item_name: "",
						balances: {},
						total: 0,
						is_new: true
					};
					// Initialize balances for currently selected warehouses
					this.filters.warehouses.forEach(wh => {
						newItem.balances[wh] = 0;
					});
					this.stockData.unshift(newItem);
					this.activeSearchRow = newItem;
				},

				onItemSearchFocus(item) {
					this.activeSearchRow = item;
					if (item.item_code) {
						this.onItemSearchInput(item);
					}
				},

				async onItemSearchInput(item) {
					if (!item.item_code || item.item_code.length < 2) {
						this.searchResults = [];
						return;
					}
					try {
						const response = await frappe.call({
							method: 'frappe.client.get_list',
							args: {
								doctype: 'Item',
								filters: {
									item_name: ['like', `%${item.item_code}%`],
									disabled: 0
								},
								fields: ['name', 'item_name'],
								limit: 10
							}
						});
						
						// If no results by name, try by code
						if (!response.message || response.message.length === 0) {
							const resByCode = await frappe.call({
								method: 'frappe.client.get_list',
								args: {
									doctype: 'Item',
									filters: {
										name: ['like', `%${item.item_code}%`],
										disabled: 0
									},
									fields: ['name', 'item_name'],
									limit: 10
								}
							});
							this.searchResults = resByCode.message || [];
						} else {
							this.searchResults = response.message;
						}
					} catch (e) {
						console.error('Error searching items:', e);
					}
				},

				selectItem(row, selected) {
					row.item_code = selected.name;
					row.item_name = selected.item_name;
					this.activeSearchRow = null;
					this.searchResults = [];
				},

				openItemDoc(item_code) {
					frappe.set_route('Form', 'Item', item_code);
				},

				updateTotal(item) {
					item.total = Object.values(item.balances).reduce((sum, val) => sum + (Number(val) || 0), 0);
				}

			}

		}).mount('#stock-level-app');

	}

	if (!window.Vue) {

		const script = document.createElement('script');

		script.src =
			'https://unpkg.com/vue@3/dist/vue.global.js';

		script.onload = mount_vue;

		document.head.appendChild(script);

	} else {

		mount_vue();

	}

};