import axios from 'axios'

const api = axios.create({
  baseURL: 'https://reviewpulse-4xkw.onrender.com',
})

export default api
