const api = require("../../utils/api");

Page({
  data: {
    roomName: "",
    rooms: []
  },
  onShow() {
    this.loadRooms();
  },
  onRoomName(event) {
    this.setData({ roomName: event.detail.value });
  },
  async createRoom() {
    const name = this.data.roomName.trim();
    if (!name) {
      wx.showToast({ title: "请输入房间名称", icon: "none" });
      return;
    }
    try {
      const app = getApp();
      await api.createRoom({
        owner_user_id: app.globalData.userId,
        name,
        room_type: "couple"
      });
      this.setData({ roomName: "" });
      this.loadRooms();
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
    }
  },
  async loadRooms() {
    try {
      const app = getApp();
      const rooms = await api.listRooms(app.globalData.userId);
      this.setData({ rooms });
    } catch (error) {
      this.setData({ rooms: [] });
    }
  }
});

