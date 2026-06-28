/** @odoo-module **/

if (!window.swal) {
    window.swal = function (options) {
        const params = typeof options === "string" ? { text: options } : options || {};
        const message = [params.title, params.text].filter(Boolean).join("\n\n");
        window.alert(message);
        return Promise.resolve();
    };
}
