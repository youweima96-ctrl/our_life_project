Page({
  data: {
    userView: ""
  },
  onInput(event) {
    this.setData({ userView: event.detail.value });
  }
});

