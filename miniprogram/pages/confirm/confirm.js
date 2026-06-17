const api = require("../../utils/api");

Page({
  data: {
    eventId: null,
    form: {
      title: "",
      summary: "",
      event_type: "other",
      topic_tags: [],
      emotion_tags: [],
      need_tags: [],
      visibility: "private"
    },
    questions: [],
    loading: false
  },
  onLoad() {
    const draft = getApp().globalData.currentDraft;
    if (!draft) {
      wx.navigateBack();
      return;
    }
    const extraction = draft.extraction.output_json;
    this.setData({
      eventId: draft.event.id,
      form: {
        title: extraction.title,
        summary: extraction.summary,
        event_type: extraction.event_type,
        topic_tags: extraction.topic_tags,
        emotion_tags: extraction.emotion_tags,
        need_tags: extraction.need_tags,
        visibility: extraction.suggested_visibility
      },
      questions: extraction.follow_up_questions
    });
  },
  onFieldInput(event) {
    const field = event.currentTarget.dataset.field;
    this.setData({ [`form.${field}`]: event.detail.value });
  },
  async confirm() {
    this.setData({ loading: true });
    try {
      await api.confirmEvent(this.data.eventId, this.data.form);
      wx.showToast({ title: "已保存" });
      wx.switchTab({ url: "/pages/records/records" });
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  },
  goBack() {
    wx.navigateBack();
  }
});

