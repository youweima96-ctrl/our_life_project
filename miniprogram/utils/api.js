const { BASE_URL } = require("./config");

function request(path, method = "GET", data = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${path}`,
      method,
      data,
      header: {
        "content-type": "application/json"
      },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject(new Error(res.data && res.data.detail ? res.data.detail : "请求失败"));
        }
      },
      fail: reject
    });
  });
}

module.exports = {
  createDraft(data) {
    return request("/events/draft", "POST", data);
  },
  confirmEvent(eventId, data) {
    return request(`/events/${eventId}/confirm`, "POST", data);
  },
  listEvents(userId) {
    return request(`/events?user_id=${userId}`);
  },
  createRoom(data) {
    return request("/rooms", "POST", data);
  },
  listRooms(userId) {
    return request(`/rooms?user_id=${userId}`);
  },
  joinRoom(data) {
    return request("/rooms/join", "POST", data);
  },
  createConflict(data) {
    return request("/conflicts", "POST", data);
  },
  generateConflictReview(conflictId) {
    return request(`/conflicts/${conflictId}/generate-review`, "POST", {});
  },
  personalWeekly(data) {
    return request("/reports/personal-weekly", "POST", data);
  }
};
