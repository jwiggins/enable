//
//  EnGraphicsContext.h
//  enable_app
//
//  Created by John Wiggins on 10/19/11.
//  Copyright 2011 Enthought. All rights reserved.
//

#import <QuartzCore/QuartzCore.h>


@protocol EnGraphicsContext

@property (nonatomic, strong) NSString *contextId;
@property (nonatomic, strong) CALayer *layer;

@end
