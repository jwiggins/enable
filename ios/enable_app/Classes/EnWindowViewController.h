//
//  EnWindowViewController.h
//  enable_app
//
//  Created by John Wiggins on 11/2/11.
//  Copyright (c) 2011 Enthought. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface EnWindowViewController : UIViewController <UIGestureRecognizerDelegate>

@property (nonatomic, strong) IBOutlet UIGestureRecognizer *panRecognizer;
@property (nonatomic, strong) IBOutlet UIGestureRecognizer *pinchRecognizer;
@property (nonatomic, strong) IBOutlet UIGestureRecognizer *tapRecognizer;
@property (nonatomic, strong) IBOutlet UIToolbar *toolbar;

- (IBAction)handlePanGesture:(UIGestureRecognizer *)gestureRecognizer;
- (IBAction)handlePinchGesture:(UIGestureRecognizer *)gestureRecognizer;
- (IBAction)handleTapGesture:(UIGestureRecognizer *)gestureRecognizer;

@end
