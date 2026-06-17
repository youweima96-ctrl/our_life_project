const api = require("../../utils/api");

Page({
  data: {
    events: []
  },
  onShow() {
    this.loadEvents();
  },
  async loadEvents() {
    try {
      const app = getApp();
      const events = await api.listEvents(app.globalData.userId);
      this.setData({ events });
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
    }
  }
});

