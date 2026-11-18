import api from "../../../services/api";

const userService = {
  register: async (data) => {
    const response = await api.post("/auth/register/", data);
    return response.data;
  },

  login: async (data) => {
    const response = await api.post("/auth/login/", data);
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get("/users/me/");
    return response.data;
  },

  updateProfile: async (data) => {
    const response = await api.put("/users/me/", data);
    return response.data;
  },
};

export default userService;
