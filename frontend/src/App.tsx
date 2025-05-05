import { Box, Container, CssBaseline, ThemeProvider, createTheme } from '@mui/material'
import { useState } from 'react'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
})

export default function App() {
  const [activeTab, setActiveTab] = useState(0)

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="xl">
        <Box sx={{ my: 4 }}>
          <h1>EngageAI</h1>
          <p>Automated social media engagement system</p>
        </Box>
      </Container>
    </ThemeProvider>
  )
}