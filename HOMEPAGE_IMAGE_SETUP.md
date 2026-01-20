# 🎨 HOMEPAGE IMAGE SETUP GUIDE

## Your New Modern Homepage is Ready! 🎉

I've redesigned your homepage with a **stunning modern carousel** inspired by professional banking websites. Now you need to add your Runda TSS student images to make it truly amazing!

## 📸 How to Add Student Images

### Step 1: Get Images from Runda TSS Website

1. Visit: **http://rundatss.rw/**
2. Look for images showing:
   - Students in classrooms
   - Students in computer labs
   - Students doing practical work
   - Campus activities
   - Graduation ceremonies
   - Group study sessions

3. **Right-click on images** and select "Save image as..."

### Step 2: Prepare Your Images

**Image Requirements:**
- Format: JPG or PNG
- Recommended size: 1920x1080px (Full HD) or 1600x900px
- File size: Keep under 500KB each for fast loading
- Content: High-quality photos of Runda TSS students

**You need 6 images total** (but can start with 3-4)

### Step 3: Rename and Save Images

Save your downloaded images with these exact names:
```
student1.jpg
student2.jpg
student3.jpg
student4.jpg
student5.jpg
student6.jpg
```

### Step 4: Copy Images to Project

**Copy all images to this folder:**
```
C:\TVETQuiz\frontend\static\images\
```

Or if your project is in a different location:
```
[YOUR_PROJECT_PATH]\frontend\static\images\
```

### Step 5: Restart Docker (if running)

```cmd
cd C:\TVETQuiz
docker-compose down
docker-compose up -d
```

### Step 6: View Your Amazing Homepage!

Open your browser and go to:
```
http://localhost:3000
```

## 🎨 What You'll See

### Modern Features:
✅ **Animated Image Carousel** - Images slide smoothly every 5 seconds
✅ **Professional Navigation** - Clean, modern header with Runda TSS branding
✅ **Gradient Overlays** - Beautiful blue gradient over images for text readability
✅ **Smooth Transitions** - Fade and slide animations between images
✅ **Interactive Indicators** - Click dots at bottom to jump to any slide
✅ **Responsive Design** - Looks perfect on phones, tablets, and computers
✅ **Feature Cards** - Animated cards showing system benefits
✅ **Stats Section** - Eye-catching statistics with hover effects
✅ **Call-to-Action** - Prominent buttons encouraging student login

## 🎯 Carousel Slides

Each image will display with:
1. **Slide 1**: "Excellence in Technical Education" - Runda TSS Building Future Leaders
2. **Slide 2**: "Hands-On Learning Experience" - Practical Skills for Real World
3. **Slide 3**: "Modern Digital Assessment" - Test Your Knowledge Anytime
4. **Slide 4**: "Collaborative Learning" - Growing Together as a Community
5. **Slide 5**: "Innovation & Technology" - Preparing for Tomorrow Today
6. **Slide 6**: "Success Stories" - Your Journey Starts Here

## 🔧 If You Don't Have Images Yet

**Don't worry!** The homepage will show beautiful gradient backgrounds as placeholders until you add real images. The system will still work perfectly.

**Temporary Solution:**
- Use any high-quality photos of students
- Use stock photos of education/learning
- Take photos at your school with permission

## 📱 Alternative: Use Your Phone

1. Take high-quality photos at Runda TSS
2. Transfer to your computer via USB or email
3. Rename and copy to the images folder
4. Restart Docker

## 🎨 Customization Options

Want to change the text on slides? Edit this file:
```
frontend\src\routes\+page.svelte
```

Look for the `slides` array around line 20:
```javascript
const slides = [
  { image: '/images/student1.jpg', title: 'Your Title', subtitle: 'Your Subtitle' },
  // ... more slides
];
```

## 🚀 Pro Tips

1. **Image Quality**: Use bright, clear photos with students' faces visible
2. **Variety**: Mix classroom, lab, outdoor, and activity photos
3. **Composition**: Choose images with space on the left for text overlay
4. **Lighting**: Well-lit photos work best
5. **Action Shots**: Students actively learning/working look more engaging

## ⚡ Quick Test Without Real Images

The homepage will work immediately with gradient placeholders. You'll see:
- Beautiful animated gradients
- All text and buttons working
- Smooth carousel transitions
- Professional layout

Just add real images when you're ready to make it even more impressive!

## 🎉 Result

Your students will be **AMAZED** by:
- Professional, modern design
- Smooth animations
- Beautiful image carousel
- Easy-to-use interface
- Fast, responsive experience

## 📞 Need Help?

If images don't show up:
1. Check file names match exactly (student1.jpg, student2.jpg, etc.)
2. Verify images are in `frontend/static/images/` folder
3. Restart Docker: `docker-compose down && docker-compose up -d`
4. Clear browser cache: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

---

**Enjoy your stunning new homepage! 🎊**
