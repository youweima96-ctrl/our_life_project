const api = require("../../utils/api");

Page({
  data: {
    loading: false,
    report: null
  },
  async generateWeekly() {
    const app = getApp();
    this.setData({ loading: true });
    try {
      const report = await api.personalWeekly({ user_id: app.globalData.userId });
      this.setData({ report });
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  }
});

