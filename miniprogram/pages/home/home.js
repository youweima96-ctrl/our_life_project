const api = require("../../utils/api");

Page({
  data: {
    rawContent: "",
    scenario: null,
    loading: false,
    events: []
  },
  onShow() {
    this.loadEvents();
  },
  onInput(event) {
    this.setData({ rawContent: event.detail.value });
  },
  chooseScenario(event) {
    this.setData({ scenario: event.currentTarget.dataset.type });
  },
  async submitRecord() {
    const app = getApp();
    const rawContent = this.data.rawContent.trim();
    if (!rawContent) {
      wx.showToast({ title: "先写一点内容", icon: "none" });
      return;
    }
    this.setData({ loading: true });
    try {
      const draft = await api.createDraft({
        user_id: app.globalData.userId,
        raw_content: rawContent,
        scenario: this.data.scenario
      });
      app.globalData.currentDraft = draft;
      this.setData({ rawContent: "", scenario: null });
      wx.navigateTo({ url: "/pages/confirm/confirm" });
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  },
  async loadEvents() {
    const app = getApp();
    try {
      const events = await api.listEvents(app.globalData.userId);
      this.setData({ events: events.slice(0, 5) });
    } catch (error) {
      this.setData({ events: [] });
    }
  }
});

