import { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  AppBar,
  Toolbar,
  IconButton,
  Snackbar
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  AutoAwesome as GenerateIcon
} from '@mui/icons-material'

interface BlogPost {
  id: string
  title: string
  content: string
  topic: string
  score?: number
}

function App() {
  const [posts, setPosts] = useState<BlogPost[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [tabValue, setTabValue] = useState(0)

  // Form state for creating/editing posts
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [currentPost, setCurrentPost] = useState<BlogPost | null>(null)
  const [formTitle, setFormTitle] = useState('')
  const [formContent, setFormContent] = useState('')
  const [formTopic, setFormTopic] = useState('')

  // Search state
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<BlogPost[]>([])

  // Generate state
  const [generateTopic, setGenerateTopic] = useState('')
  const [generatedPost, setGeneratedPost] = useState<{ title: string; content: string } | null>(null)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    fetchPosts()
  }, [])

  const fetchPosts = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/posts')
      const data = await response.json()
      setPosts(data)
    } catch (err) {
      setError('Failed to fetch posts')
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePost = () => {
    setCurrentPost(null)
    setFormTitle('')
    setFormContent('')
    setFormTopic('')
    setEditDialogOpen(true)
  }

  const handleEditPost = (post: BlogPost) => {
    setCurrentPost(post)
    setFormTitle(post.title)
    setFormContent(post.content)
    setFormTopic(post.topic)
    setEditDialogOpen(true)
  }

  const handleDeletePost = async (postId: string) => {
    try {
      await fetch(`/api/posts/delete/${postId}`)
      setSuccess('Post deleted successfully')
      fetchPosts()
    } catch (err) {
      setError('Failed to delete post')
    }
  }

  const handleSavePost = async () => {
    setLoading(true)
    try {
      if (currentPost) {
        await fetch('/api/posts/update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id: currentPost.id,
            title: formTitle,
            content: formContent,
            topic: formTopic
          })
        })
        setSuccess('Post updated successfully')
      } else {
        await fetch('/api/posts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: formTitle,
            content: formContent,
            topic: formTopic
          })
        })
        setSuccess('Post created successfully')
      }
      setEditDialogOpen(false)
      fetchPosts()
    } catch (err) {
      setError('Failed to save post')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    setLoading(true)
    try {
      const response = await fetch(`/api/posts/search/${encodeURIComponent(searchQuery)}`)
      const data = await response.json()
      setSearchResults(data)
    } catch (err) {
      setError('Search failed')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    if (!generateTopic.trim()) return
    setGenerating(true)
    setGeneratedPost(null)
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: generateTopic })
      })
      const data = await response.json()
      setGeneratedPost({ title: data.title, content: data.content })
    } catch (err) {
      setError('Failed to generate post')
    } finally {
      setGenerating(false)
    }
  }

  const handleSaveGeneratedPost = async () => {
    if (!generatedPost) return
    setLoading(true)
    try {
      await fetch('/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: generatedPost.title,
          content: generatedPost.content,
          topic: generateTopic
        })
      })
      setSuccess('Generated post saved successfully')
      setGeneratedPost(null)
      setGenerateTopic('')
      fetchPosts()
    } catch (err) {
      setError('Failed to save generated post')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Blog Post Manager
          </Typography>
          <Button color="inherit" startIcon={<AddIcon />} onClick={handleCreatePost}>
            New Post
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ mb: 3 }}>
          <Tab label="All Posts" />
          <Tab label="Search" />
          <Tab label="Generate" />
        </Tabs>

        {tabValue === 0 && (
          <Box>
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : (
              <Grid container spacing={3}>
                {posts.map((post) => (
                  <Grid item xs={12} md={6} lg={4} key={post.id}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {post.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                          Topic: {post.topic}
                        </Typography>
                        <Typography variant="body2" sx={{
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: 'vertical'
                        }}>
                          {post.content}
                        </Typography>
                      </CardContent>
                      <CardActions>
                        <IconButton size="small" onClick={() => handleEditPost(post)}>
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="error" onClick={() => handleDeletePost(post.id)}>
                          <DeleteIcon />
                        </IconButton>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        )}

        {tabValue === 1 && (
          <Box>
            <Box display="flex" gap={2} mb={3}>
              <TextField
                fullWidth
                label="Search posts"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button variant="contained" startIcon={<SearchIcon />} onClick={handleSearch}>
                Search
              </Button>
            </Box>
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : (
              <Grid container spacing={3}>
                {searchResults.map((post) => (
                  <Grid item xs={12} md={6} lg={4} key={post.id}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {post.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                          Topic: {post.topic} | Score: {post.score?.toFixed(2)}
                        </Typography>
                        <Typography variant="body2" sx={{
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: 'vertical'
                        }}>
                          {post.content}
                        </Typography>
                      </CardContent>
                      <CardActions>
                        <IconButton size="small" onClick={() => handleEditPost(post)}>
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="error" onClick={() => handleDeletePost(post.id)}>
                          <DeleteIcon />
                        </IconButton>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        )}

        {tabValue === 2 && (
          <Box>
            <Box display="flex" gap={2} mb={3}>
              <TextField
                fullWidth
                label="Enter a topic"
                value={generateTopic}
                onChange={(e) => setGenerateTopic(e.target.value)}
                placeholder="e.g., machine learning, climate change, productivity tips"
              />
              <Button
                variant="contained"
                startIcon={generating ? <CircularProgress size={20} color="inherit" /> : <GenerateIcon />}
                onClick={handleGenerate}
                disabled={generating}
              >
                Generate
              </Button>
            </Box>
            {generatedPost && (
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h5" gutterBottom>
                    {generatedPost.title}
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {generatedPost.content}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleSaveGeneratedPost}
                    disabled={loading}
                  >
                    Save Post
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => setGeneratedPost(null)}
                  >
                    Discard
                  </Button>
                </CardActions>
              </Card>
            )}
          </Box>
        )}
      </Container>

      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{currentPost ? 'Edit Post' : 'Create New Post'}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Title"
            fullWidth
            value={formTitle}
            onChange={(e) => setFormTitle(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Topic"
            fullWidth
            value={formTopic}
            onChange={(e) => setFormTopic(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Content"
            fullWidth
            multiline
            rows={8}
            value={formContent}
            onChange={(e) => setFormContent(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSavePost} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess(null)}
      >
        <Alert severity="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default App
