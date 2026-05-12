from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from PIL import Image
import io

from .models import Project, ProjectStep, ProjectFeature
from apps.courses.models import Technology

User = get_user_model()


class ProjectModelTests(TestCase):
    """Test cases for Project model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.tech = Technology.objects.create(name='Python')
        
    def test_project_creation(self):
        """Test creating a project"""
        project = Project.objects.create(
            title='Test Project',
            description='A test project description',
            difficulty='beginner',
            github_url='https://github.com/test/project',
            demo_url='https://demo.example.com',
            is_published=True
        )
        project.technologies.add(self.tech)
        
        self.assertEqual(project.title, 'Test Project')
        self.assertEqual(project.difficulty, 'beginner')
        self.assertTrue(project.is_published)
        self.assertEqual(project.technologies.count(), 1)
        self.assertIsNotNone(project.slug)
        
    def test_project_slug_generation(self):
        """Test automatic slug generation"""
        project = Project.objects.create(
            title='Test Project Title',
            description='Test description',
            difficulty='beginner'
        )
        self.assertEqual(project.slug, 'test-project-title')
        
    def test_project_properties(self):
        """Test project properties"""
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            difficulty='beginner'
        )
        
        # Test total_steps property
        self.assertEqual(project.total_steps, 0)
        
        # Add steps and test again
        ProjectStep.objects.create(
            project=project,
            title='Step 1',
            duration=30,
            order=1
        )
        ProjectStep.objects.create(
            project=project,
            title='Step 2',
            duration=45,
            order=2
        )
        
        self.assertEqual(project.total_steps, 2)
        self.assertEqual(project.total_duration_str, '1 soat 15 daqiqa')


class ProjectAPITests(APITestCase):
    """Test cases for Project API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Create technologies
        self.tech1 = Technology.objects.create(name='Python')
        self.tech2 = Technology.objects.create(name='Django')
        
        # Create projects
        self.published_project = Project.objects.create(
            title='Published Project',
            description='A published project',
            difficulty='beginner',
            github_url='https://github.com/test/published',
            demo_url='https://demo.example.com',
            is_published=True
        )
        self.published_project.technologies.add(self.tech1, self.tech2)
        
        # Add steps and features to published project
        ProjectStep.objects.create(
            project=self.published_project,
            title='Step 1',
            video_url='https://example.com/video1.mp4',
            duration=30,
            order=1
        )
        ProjectFeature.objects.create(
            project=self.published_project,
            text='Feature 1',
            order=1
        )
        
        self.draft_project = Project.objects.create(
            title='Draft Project',
            description='A draft project',
            difficulty='advanced',
            is_published=False
        )
        
        # Create temporary image for upload tests
        self.image = self.create_test_image()
        
    def create_test_image(self):
        """Create a test image file"""
        image = Image.new('RGB', (100, 100), 'red')
        image_io = io.BytesIO()
        image.save(image_io, 'JPEG')
        image_io.seek(0)
        # Give the image a proper name with extension
        image_io.name = 'test_image.jpg'
        return image_io
        
    def authenticate(self):
        """Authenticate the client with JWT token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
    def test_project_list_view(self):
        """Test GET /projects endpoint"""
        url = reverse('project-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only published projects
        self.assertEqual(response.data['results'][0]['title'], 'Published Project')
        self.assertEqual(response.data['results'][0]['difficulty'], 'beginner')
        self.assertEqual(len(response.data['results'][0]['technologies']), 2)
        
    def test_project_list_filtering(self):
        """Test filtering options for project list"""
        url = reverse('project-list')
        
        # Test difficulty filter
        response = self.client.get(url, {'difficulty': 'beginner'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test technology filter
        response = self.client.get(url, {'technologies': self.tech1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test search
        response = self.client.get(url, {'search': 'Published'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test ordering
        response = self.client.get(url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_project_detail_view(self):
        """Test GET /projects/{id} endpoint"""
        url = reverse('project-detail', kwargs={'pk': self.published_project.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Published Project')
        self.assertEqual(response.data['difficulty'], 'beginner')
        self.assertEqual(len(response.data['technologies']), 2)
        self.assertEqual(len(response.data['steps']), 1)
        self.assertEqual(len(response.data['features']), 1)
        self.assertEqual(response.data['total_steps'], 1)
        
    def test_project_detail_view_not_published(self):
        """Test that draft projects are not accessible"""
        url = reverse('project-detail', kwargs={'pk': self.draft_project.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_project_create_view(self):
        """Test POST /projects/admin/create endpoint"""
        self.authenticate()
        url = reverse('project-create')
        
        data = {
            'title': 'New Project',
            'description': 'A new project description',
            'difficulty': 'intermediate',
            'github_url': 'https://github.com/test/new',
            'demo_url': 'https://demo.new.com',
            'technologies': [self.tech1.id],
            'is_published': True
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 3)
        new_project = Project.objects.get(title='New Project')
        self.assertEqual(new_project.difficulty, 'intermediate')
        self.assertTrue(new_project.is_published)
        
    def test_project_create_view_unauthorized(self):
        """Test that unauthenticated users cannot create projects"""
        url = reverse('project-create')
        data = {
            'title': 'Unauthorized Project',
            'description': 'Should not be created',
            'difficulty': 'beginner'
        }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Project.objects.count(), 2)  # No new project created
        
    def test_project_create_with_image(self):
        """Test creating a project with image upload"""
        self.authenticate()
        url = reverse('project-create')
        
        data = {
            'title': 'Project with Image',
            'description': 'Project with uploaded image',
            'difficulty': 'intermediate',
            'image': self.image,
            'is_published': True
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_project = Project.objects.get(title='Project with Image')
        self.assertTrue(new_project.image)
        # Check that image name is set (not trying to access path)
        self.assertTrue(new_project.image.name)
        
    def test_project_update_view(self):
        """Test PUT /projects/admin/{id}/update endpoint"""
        self.authenticate()
        url = reverse('project-update', kwargs={'pk': self.published_project.pk})
        
        data = {
            'title': 'Updated Project',
            'description': 'Updated description',
            'difficulty': 'advanced',
            'github_url': 'https://github.com/test/updated',
            'technologies': [self.tech2.id],
            'is_published': True
        }
        
        response = self.client.put(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.published_project.refresh_from_db()
        self.assertEqual(self.published_project.title, 'Updated Project')
        self.assertEqual(self.published_project.difficulty, 'advanced')
        self.assertEqual(self.published_project.technologies.count(), 1)
        self.assertEqual(self.published_project.technologies.first().name, 'Django')
        
    def test_project_update_view_patch(self):
        """Test PATCH /projects/admin/{id}/update endpoint"""
        self.authenticate()
        url = reverse('project-update', kwargs={'pk': self.published_project.pk})
        
        data = {
            'title': 'Partially Updated Project'
        }
        
        response = self.client.patch(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.published_project.refresh_from_db()
        self.assertEqual(self.published_project.title, 'Partially Updated Project')
        # Other fields should remain unchanged
        self.assertEqual(self.published_project.difficulty, 'beginner')
        
    def test_project_update_with_new_image(self):
        """Test updating project with new image"""
        self.authenticate()
        url = reverse('project-update', kwargs={'pk': self.published_project.pk})
        
        # First, set an initial image
        self.published_project.image.save('initial.jpg', self.image, save=True)
        
        data = {
            'title': 'Project with New Image',
            'image': self.create_test_image()
        }
        
        response = self.client.patch(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.published_project.refresh_from_db()
        self.assertEqual(self.published_project.title, 'Project with New Image')
        # Verify image was updated (check name instead of path)
        self.assertTrue(self.published_project.image.name)
        self.assertNotEqual(self.published_project.image.name, 'initial.jpg')
        
    def test_project_update_without_image(self):
        """Test updating project without providing image (should keep existing)"""
        self.authenticate()
        url = reverse('project-update', kwargs={'pk': self.published_project.pk})
        
        data = {
            'title': 'Updated Title Only'
        }
        
        response = self.client.patch(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.published_project.refresh_from_db()
        self.assertEqual(self.published_project.title, 'Updated Title Only')
        
    def test_project_update_view_unauthorized(self):
        """Test that unauthenticated users cannot update projects"""
        url = reverse('project-update', kwargs={'pk': self.published_project.pk})
        data = {'title': 'Unauthorized Update'}
        
        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_project_delete_view(self):
        """Test DELETE /projects/admin/{id}/delete endpoint"""
        self.authenticate()
        url = reverse('project-delete', kwargs={'pk': self.draft_project.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 1)  # Only published project remains
        self.assertFalse(Project.objects.filter(pk=self.draft_project.pk).exists())
        
    def test_project_delete_view_unauthorized(self):
        """Test that unauthenticated users cannot delete projects"""
        url = reverse('project-delete', kwargs={'pk': self.published_project.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Project.objects.count(), 2)  # No project deleted
        
    def test_project_pagination(self):
        """Test pagination functionality"""
        # Create more projects for pagination testing
        for i in range(15):
            Project.objects.create(
                title=f'Project {i}',
                description=f'Description {i}',
                difficulty='beginner',
                is_published=True
            )
        
        url = reverse('project-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertLessEqual(len(response.data['results']), 12)  # Default page size
        
    def test_project_list_empty_database(self):
        """Test project list with no published projects"""
        Project.objects.all().delete()
        
        url = reverse('project-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.data['count'], 0)
